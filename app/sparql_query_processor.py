import json
import os
import time
from typing import TYPE_CHECKING, Dict, List

import numpy as np
import requests
from jinja2 import Environment, FileSystemLoader
from models import TEMPLATE_REGISTRY
from sentence_transformers import SentenceTransformer

if TYPE_CHECKING:
    from models.templates import BaseTemplate


class SPARQLQueryProcessor:
    def __init__(self, templates_dir: str, fuseki_endpoint: str, ollama_host: str = "http://localhost:11434"):
        self.fuseki_endpoint = fuseki_endpoint
        self.ollama_host = ollama_host
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        # Initialize embedding model with specific model name
        self.embedding_model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1') # all-MiniLM-L6-v2
        
        # Load or compute template embeddings
        data_dir = os.path.join(os.path.dirname(templates_dir), 'data')
        self.embeddings_file = os.path.join(data_dir, 'template_embeddings.json')
        self.template_embeddings = self._load_or_compute_embeddings()
    
    def _load_or_compute_embeddings(self) -> Dict[str, np.ndarray]:
        """Load existing embeddings or compute new ones if not found."""
        # Always recompute embeddings to ensure consistency
        if not os.path.exists(self.embeddings_file):
            print("No template embedding file found, creating new embeddings...")
            embeddings = self._compute_template_embeddings()
            self._save_embeddings(embeddings)
        else:
            with open(self.embeddings_file) as embedding_file:
                embeddings = json.load(embedding_file)
        return embeddings
    
    def _save_embeddings(self, embeddings: Dict[str, np.ndarray]) -> None:
        """Save embeddings to file."""
        # Convert numpy arrays to lists for JSON serialization
        embeddings_dict = {k: v.tolist() for k, v in embeddings.items()}
        os.makedirs(os.path.dirname(self.embeddings_file), exist_ok=True)
        with open(self.embeddings_file, 'w') as f:
            json.dump(embeddings_dict, f, indent=4)
    
    def _compute_template_embeddings(self) -> Dict[str, np.ndarray]:
        """Compute embeddings for all template descriptions."""
        embeddings = {}
        for template in TEMPLATE_REGISTRY.values():
            description = template.template_description
            field_info = template.get_fields_info()
            context = description + "\nFields:\n" + "\n".join(
                f"- {k}: {v}" for k, v in field_info.items()
            )
            embedding = self.embedding_model.encode(context)
            embeddings[template.template_name] = embedding
        return embeddings
    
    def validate_template(self, user_prompt, template):
        template_description = template.template_description
        temlate_params = template.get_fields_info()

        prompt = f"""You are validator of templates. In our scenario we have a template which should be strictly related to user prompt. You will be given user prompt and a tamplate description in raw text and template parameter names along with their description.

User Query: {user_prompt};
Template Description: {template_description};
Template Parameters with Descriptions: {temlate_params}

Instructions: Return your answer in exactly one word. Response with Yes or No.


"""
        try:
            response = self._call_ollama(prompt)
            if response == "Yes":
                return True
            else:
                return False
        except Exception as e:
            return str(e)

    def find_best_template(self, user_query: str) -> Dict:
        """Find the most relevant template for the user query."""
        query_embedding = self.embedding_model.encode(user_query)
        
        scores = np.array([])
        templates = np.array([])
        
        for template_id, template_embedding in self.template_embeddings.items():
            similarity = np.dot(query_embedding, template_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(template_embedding)
            )
            scores = np.append(scores, similarity)
            templates = np.append(templates, TEMPLATE_REGISTRY[template_id])

        templates = templates[np.argsort(scores)[::-1]]
    
        template = None
        for id, init_template in enumerate(templates):
            validation_result = self.validate_template(user_query, init_template)
            if validation_result is False:
                validation_result = self.validate_template(user_query, init_template)
                if validation_result is False:
                    continue
            if validation_result is True:
                template = init_template
                break
        
        return template
    
    def _call_ollama(self, prompt: str, max_retries: int = 3, timeout: int = 60) -> str:
        """Make a direct HTTP call to Ollama API with retries."""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "llama2", # FIXME:  not to be hardcoded!!!
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=timeout
                )
                response.raise_for_status()
                return response.json()['response']
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Timeout occurred, retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)  # Wait before retrying
                    continue
                raise
            except Exception as e:
                print(f"Error connecting to Ollama: {str(e)}")
                print("Please ensure Ollama is running and accessible at the configured host")
                raise
    
    def extract_parameters(self, user_query: str, template: Dict) -> Dict[str, str]:
        """Extract parameters from user query using Ollama."""
        prompt = f"""You are a parameter extraction assistant. Your task is to extract specific parameters from a user query and return them in JSON format.

Required parameters:
{json.dumps(template.get_fields(), indent=2)}
Parameters descriptions:
{json.dumps(template.get_fields_info(), indent=2)}

User query: {user_query}

Instructions:
1. Extract ONLY the parameters listed above
2. Return ONLY a valid JSON object with the extracted parameters
3. Ensure the extracted parameters have the correct format specified in the description
4. Do not include any other text or explanation
5. If a parameter is not found, omit it from the JSON
"""
        try:
            response = self._call_ollama(prompt)
            # Clean the response to ensure it's valid JSON
            response = response.strip()
            if not response.startswith('{'):
                response = response[response.find('{'):]
            if not response.endswith('}'):
                response = response[:response.rfind('}')+1]
            return json.loads(response)
        except Exception as e:
            print(f"Error extracting parameters: {str(e)}")
            return {}
    
    def execute_query(self, valid_template: "BaseTemplate") -> List[Dict]:
        """Execute the SPARQL query with the given parameters."""
        parameters = valid_template.model_dump()
        print(f"---TEMPLATE---\n{valid_template.template_name}")
        template = self.env.get_template(valid_template.template_path)
        query = template.render(**parameters)
        
        # Print the populated SPARQL query
        print("\nGenerated SPARQL Query:")
        print("------------------------")
        print(query)
        print("------------------------\n")
        
        # Use the /sparql endpoint instead of /query
        sparql_endpoint = self.fuseki_endpoint.replace('/query', '/sparql')
        
        response = requests.get(
            sparql_endpoint,
            params={'query': query},
            headers={'Accept': 'application/sparql-results+json'}
        )
        
        if response.status_code == 200:
            return response.json()['results']['bindings']
        else:
            raise Exception(f"Query execution failed: {response.text}")
    
    def generate_response(self, query_results: List[Dict], user_query: str) -> str:
        """Generate a natural language response using Ollama."""
        prompt = f"""You are a helpful assistant that provides clear and concise answers based on query results.

User question: {user_query}

Query results: {json.dumps(query_results, indent=2)}

Instructions:
1. Provide a direct answer to the user's question
2. Use the query results to support your answer
3. Keep the response concise and clear
4. If there are no results, say so clearly

Answer:"""
        
        try:
            return self._call_ollama(prompt)
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "Error generating response. Please check if Ollama is running."
    
    def process_query(self, user_query: str) -> str:
        """Process a user query end-to-end."""
        # Find the best matching template
        template = self.find_best_template(user_query)
        if not template:
            return "CONTINUE", "I couldn't find a suitable query template for your question."
        
        # Extract parameters
        parameters = self.extract_parameters(user_query, template)
        parameters = {key: str(value) for key, value in parameters.items()}
        print(f"Extracted parameters: {parameters}")
        parameterized_template, errors, missing = template.create_and_validate(parameters)
        if parameterized_template:
            print(f"✅ Success! Instance created: {parameterized_template}")
        else:
            print("❌ Failure!")

        msg = ''
        if missing:
            missing_params_with_desc = [f"{k} - {v}" for k, v in template.get_fields_info().items() if k in missing]
            msg += f"Please provide the following information: {', '.join(missing_params_with_desc)}\n"
        if errors:
            errors_with_desc = '\n'.join(f'{k}: {v}' for k, v in errors.items())
            msg += f"Some parameters are invalid: {parameters}\n"
            msg += f"Errors: {errors_with_desc}"
            msg += "\nPlease try to provide these parameters in a correct format."
        if msg:
            return "CONTINUE", msg
        
        # Execute query
        try:
            results = self.execute_query(parameterized_template)
            return "RESET", self.generate_response(results, user_query)
        except Exception as e:
            return "RESET", f"Error processing your query: {str(e)}."
