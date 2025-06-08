import streamlit as st
import requests
import json
from typing import List, Dict

# Configuration
FUSEKI_HOST = "localhost"
FUSEKI_PORT = 3030

# Set page config to show title in navigation bar
st.set_page_config(
    page_title="GraphRAG Chat Interface",
    page_icon="💬",
    layout="wide"
)

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

def get_basic_response(query: str, dataset: str, response_format: str, show_sparql: bool, show_table: bool, table_limit: int) -> str:
    """Generate a basic response for the chat interface."""
    # This is a placeholder - you can enhance this later
    response = f"I received your query about dataset '{dataset}': {query}\n\n"
    
    if show_sparql:
        # Placeholder for actual SPARQL query
        response += "Generated SPARQL query:\n```sparql\nSELECT ?s ?p ?o WHERE { ?s ?p ?o }\n```\n\n"
    
    response += "This is a placeholder response. The actual response logic will be implemented later."
    
    if response_format == "Detailed":
        response += "\n\nAdditional details would be shown here..."
    elif response_format == "Concise":
        response = response.split("\n\n")[0]  # Just show the first part
    
    return response

def main():
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
            response = get_basic_response(prompt, selected_dataset, response_format, show_sparql, show_table, table_limit)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 