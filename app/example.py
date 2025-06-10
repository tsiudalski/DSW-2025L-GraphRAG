import json
import os
import sys

import requests
from dotenv import load_dotenv
from sparql_query_processor import SPARQLQueryProcessor

# Load environment variables from .env file if it exists
load_dotenv()

def test_ollama_connection(ollama_url):
    """Test connection to Ollama service"""
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llama2",
                "prompt": "test",
                "stream": False
            },
            timeout=200
        )
        response.raise_for_status()
        print("✅ Successfully connected to Ollama")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Ollama at {ollama_url}")
        print(f"Error: {str(e)}")
        if "Connection refused" in str(e):
            print("Please ensure Ollama is running and the port is correct")
        return False

def test_fuseki_connection(fuseki_url):
    """Test connection to Fuseki service"""
    try:
        # Test with a simple SPARQL query
        response = requests.get(
            fuseki_url.replace('/query', '/sparql'),
            params={'query': 'SELECT * WHERE { ?s ?p ?o } LIMIT 1'},
            headers={'Accept': 'application/sparql-results+json'},
            # timeout=5
        )
        response.raise_for_status()
        print("✅ Successfully connected to Fuseki")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Fuseki at {fuseki_url}")
        print(f"Error: {str(e)}")
        if "Connection refused" in str(e):
            print("Please ensure Fuseki is running and the port is correct")
        return False

def main():
    # Initialize the processor with absolute path
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get configuration from environment variables with defaults
    fuseki_host = os.getenv('FUSEKI_HOST', 'localhost')
    fuseki_port = os.getenv('FUSEKI_PORT', '3030')
    
    # The test will target a specific dataset, e.g., 'office-test'.
    # You can set DATASET_NAME in a .env file to change this.
    dataset_name = os.getenv('DATASET_NAME', 'ds')
    
    ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
    ollama_port = os.getenv('OLLAMA_PORT', '11434')

    # Construct the correct Fuseki URL for the specific dataset, ending in /query
    # as expected by the SPARQLQueryProcessor's internal logic.
    fuseki_url = f'http://{fuseki_host}:{fuseki_port}/{dataset_name}/query'
    ollama_url = f'http://{ollama_host}:{ollama_port}'

    print(f"Connecting to Fuseki at: {fuseki_url}")
    print(f"Connecting to Ollama at: {ollama_url}")

    # Test connections before proceeding
    if not test_fuseki_connection(fuseki_url):
        print("Exiting due to Fuseki connection failure")
        sys.exit(1)
    
    if not test_ollama_connection(ollama_url):
        print("Exiting due to Ollama connection failure")
        sys.exit(1)

    processor = SPARQLQueryProcessor(
        templates_dir=os.path.join(app_dir, 'templates'),
        fuseki_endpoint=fuseki_url,
        ollama_host=ollama_url
    )

    # Example queries
    queries = [
        "How many rooms does the 7th floor have?",
        'What was the average temperature for the R5 154 sensor during the first week of May 2022?',
        "What was the last reported CO2 level from R5 95 device?"
    ]

    # Process each query
    for query in queries:
        print(f"\nProcessing query: {query}")
        try:
            response = processor.process_query(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error processing query: {str(e)}")


if __name__ == "__main__":
    main()
