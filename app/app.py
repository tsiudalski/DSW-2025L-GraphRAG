import streamlit as st
import requests
import json
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from sparql_query_processor import SPARQLQueryProcessor
from models import TEMPLATE_REGISTRY # Removed to break circular dependency

# Set page config to show title in navigation bar
st.set_page_config(
    page_title="GraphRAG Chat Interface",
    page_icon="💬",
    layout="wide"
)

# Add parent directory to Python path for imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Load environment variables
load_dotenv()

# Configuration
FUSEKI_HOST = os.getenv('FUSEKI_HOST', 'localhost')
FUSEKI_PORT = os.getenv('FUSEKI_PORT', '3030')
FUSEKI_ENDPOINT = os.getenv('FUSEKI_ENDPOINT', 'demo7floor')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')

# --- Initialization of SPARQLQueryProcessor --- #
# This must be done only once per app run, usually outside of functions or in st.session_state

def get_available_datasets() -> List[Dict]:
    """Get list of available datasets from Fuseki."""
    try:
        response = requests.get(
            f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/$/datasets",
            headers={"Accept": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("datasets", [])
        else:
            st.error(f"Failed to fetch datasets: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to Fuseki: {str(e)}")
        return []

def get_dataset_name(dataset: Dict) -> str:
    """Extract dataset name from dataset info."""
    return dataset.get("ds.name", "").strip("/")

def get_basic_response(query: str, dataset: str, 
                       response_format: str, show_sparql: bool,
                       show_table: bool, table_limit: int) -> str:
    """Generate a response using SPARQLQueryProcessor."""
    try:
        processor = st.session_state.processor
        status, response = processor.process_query(query)
        
        if status == "RESET":
            return response
        elif status == "CONTINUE":
            return response + "\n\nPlease continue your query..."
        else:
            return f"Error processing query: {response}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Initialize processor if not already in session state
    if 'processor' not in st.session_state:
        fuseki_url = f'http://{FUSEKI_HOST}:{FUSEKI_PORT}/{FUSEKI_ENDPOINT}/query'
        ollama_url = f'http://{OLLAMA_HOST}:{OLLAMA_PORT}'
        print(fuseki_url)
        st.session_state.processor = SPARQLQueryProcessor(
            templates_dir=os.path.join(app_dir, 'templates'),
            fuseki_endpoint=fuseki_url,
            ollama_host=ollama_url
        )

    # Get available datasets
    datasets = get_available_datasets()
    
    if not datasets:
        st.warning("No datasets available. Please create a dataset first.")
        return
    
    # Create options in the sidebar
    with st.sidebar:
        st.header("Dataset Selection")
        dataset_names = [get_dataset_name(ds) for ds in datasets]
        selected_dataset = st.selectbox(
            "Select Dataset",
            dataset_names,
            index=0 if dataset_names else None,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.header("Response Settings")
        response_format = st.radio(
            "Response Format",
            ["Detailed", "Standard", "Concise"],
            index=1,
            help="Choose how detailed you want the responses to be"
        )
        
        show_sparql = st.checkbox(
            "Show SPARQL Query",
            value=False,
            help="Display the generated SPARQL query in the response"
        )
        
        show_table = st.checkbox(
            "View Output Table",
            value=False,
            help="Display results in a table format"
        )
        
        if show_table:
            table_limit = st.number_input(
                "Table Record Limit",
                min_value=1,
                max_value=1000,
                value=100,
                step=1,
                help="Maximum number of records to show in the table"
            )
        else:
            table_limit = 100  # Default value
        
        st.markdown("---")
        
        st.header("History")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = """👋 Welcome to GraphRAG Chat Interface!

I can help you explore and query your RDF datasets using natural language. Here's what you can do:

1. Select a dataset from the dropdown in the sidebar
2. Ask questions about your data in the chat below
3. See the answer and optionally view the generated SPARQL queries and/or output table

Try asking a question about your selected dataset!"""
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your dataset"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # First get the SPARQL query if needed
                if show_sparql:
                    processor = st.session_state.processor
                    template = processor.find_best_template(prompt)
                    if template:
                        parameters = processor.extract_parameters(prompt, template)
                        parameters = {key: str(value) for key, value in parameters.items()}
                        parameterized_template, errors, missing = template.create_and_validate(parameters)
                        if parameterized_template:
                            template = processor.env.get_template(parameterized_template.template_path)
                            sparql_query = template.render(**parameters)
                            with st.expander("View SPARQL Query", expanded=False):
                                st.code(f"# Template: {parameterized_template.template_name}\n{sparql_query}", language="sparql")
                
                # Then get the actual response
                response = get_basic_response(prompt, selected_dataset, response_format, show_sparql, show_table, table_limit)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 