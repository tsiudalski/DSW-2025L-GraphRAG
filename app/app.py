import streamlit as st
import requests
import json
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from sparql_query_processor import SPARQLQueryProcessor
from models import TEMPLATE_REGISTRY  # Removed to break circular dependency

# Set page config to show title in navigation bar
st.set_page_config(page_title="GraphRAG Chat Interface", page_icon="💬", layout="wide")

# Add parent directory to Python path for imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.append(app_dir)

# Load environment variables
load_dotenv()

# Configuration
FUSEKI_HOST = os.getenv("FUSEKI_HOST", "localhost")
FUSEKI_PORT = os.getenv("FUSEKI_PORT", "3030")
FUSEKI_ENDPOINT = os.getenv("FUSEKI_ENDPOINT", "demo7floor")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")

# --- Initialization of SPARQLQueryProcessor --- #
# This must be done only once per app run, usually outside of functions or in st.session_state


def get_available_datasets() -> List[Dict]:
    """Get list of available datasets from Fuseki."""
    try:
        response = requests.get(
            f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/$/datasets",
            headers={"Accept": "application/json"},
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


def get_basic_response(
    query: str,
    dataset: str,
    response_format: str,
    show_sparql: bool,
    show_table: bool,
    table_limit: int,
) -> str:
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
    if "processor" not in st.session_state:
        fuseki_url = f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/{FUSEKI_ENDPOINT}/query"
        ollama_url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
        print(fuseki_url)
        st.session_state.processor = SPARQLQueryProcessor(
            templates_dir=os.path.join(app_dir, "templates"),
            fuseki_endpoint=fuseki_url,
            ollama_host=ollama_url,
        )

    # Get available datasets
    datasets = get_available_datasets()

    if not datasets:
        st.warning("No datasets available. Please create a dataset first.")
        return

    # Create options in the sidebar
    with st.sidebar:
        st.header("📦 Dataset Selection")
        dataset_names = [get_dataset_name(ds) for ds in datasets]
        selected_dataset = st.selectbox(
            "Select Dataset",
            dataset_names,
            index=0 if dataset_names else None,
            label_visibility="collapsed",
        )

        st.header("💬 Response Settings")
        response_format = "Standard"  # fixed to Standard format

        show_sparql = st.checkbox(
            "Show SPARQL Query",
            value=True,
            help="Display the generated SPARQL query in the response",
        )

        if show_sparql:
            show_prefixes = st.checkbox(
                "Show PREFIX Declarations",
                value=False,
                help="Include PREFIX declarations in the displayed SPARQL query",
            )

        show_table = st.checkbox(
            "View Output Table", value=False, help="Display results in a table format"
        )

        if show_table:
            table_limit = st.number_input(
                "Table Record Limit",
                min_value=1,
                max_value=1000,
                value=100,
                step=1,
                help="Maximum number of records to show in the table",
            )
        else:
            table_limit = 100  # Default value

        st.header("History")
        if st.button("🗑️ Clear Chat History"):
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
        st.session_state.messages.append(
            {"role": "assistant", "content": welcome_message}
        )

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
                processor = st.session_state.processor
                template = processor.find_best_template(prompt)
                print(f"Template: {template.template_name}")
                if template:
                    parameters = processor.extract_parameters(prompt, template)
                    parameters = {key: str(value) for key, value in parameters.items()}
                    print(f"Params: {parameters}")
                    parameterized_template, errors, missing = (
                        template.create_and_validate(parameters)
                    )

                    if parameterized_template:
                        # Get the SPARQL query if needed
                        if show_sparql:
                            template = processor.env.get_template(
                                parameterized_template.template_path
                            )
                            validated_parameters = parameterized_template.model_dump()
                            sparql_query = template.render(**validated_parameters)
                            # Remove PREFIX declarations and empty lines from the query if not showing prefixes
                            if not show_prefixes:
                                query_without_prefixes = "\n".join(
                                    line
                                    for line in sparql_query.split("\n")
                                    if not line.strip().startswith("PREFIX")
                                    and line.strip()
                                )
                            else:
                                # Split query into prefixes and main query
                                lines = sparql_query.split("\n")
                                prefix_lines = [
                                    line
                                    for line in lines
                                    if line.strip().startswith("PREFIX")
                                ]
                                query_lines = [
                                    line
                                    for line in lines
                                    if not line.strip().startswith("PREFIX")
                                    and line.strip()
                                ]
                                # Join with an extra blank line between prefixes and query
                                query_without_prefixes = (
                                    "\n".join(prefix_lines)
                                    + "\n\n"
                                    + "\n".join(query_lines)
                                )
                            with st.expander("View SPARQL Query", expanded=False):
                                st.code(
                                    f"# Template: {parameterized_template.template_name}\n{query_without_prefixes}",
                                    language="sparql",
                                )

                        # Execute query and get results
                        try:
                            results = processor.execute_query(parameterized_template)

                            # Show table if requested
                            if show_table and results:
                                with st.expander("View Results Table", expanded=False):
                                    # Convert results to DataFrame format
                                    if results:
                                        # Get all unique column names from the results
                                        columns = set()
                                        for result in results:
                                            columns.update(result.keys())

                                        # Create a list of dictionaries for DataFrame
                                        table_data = []
                                        for result in results[
                                            :table_limit
                                        ]:  # Apply row limit
                                            row = {}
                                            for col in columns:
                                                # Handle missing values and extract the 'value' from the binding
                                                row[col] = result.get(col, {}).get(
                                                    "value", ""
                                                )
                                            table_data.append(row)

                                        # Display the table
                                        st.dataframe(
                                            table_data,
                                            use_container_width=True,
                                            hide_index=True,
                                        )

                            # Generate and show the response
                            response_placeholder = st.empty()
                            full_response = ""

                            # Stream the response from Ollama
                            for chunk in processor.generate_response_stream(
                                results, prompt
                            ):
                                full_response += chunk
                                response_placeholder.markdown(full_response + "▌")

                            # Show final response without the cursor
                            response_placeholder.markdown(full_response)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": full_response}
                            )

                        except Exception as e:
                            error_msg = f"Error processing your query: {str(e)}"
                            st.error(error_msg)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": error_msg}
                            )
                    else:
                        error_msg = "Could not validate the query parameters. Please check your input."
                        st.error(error_msg)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_msg}
                        )
                else:
                    error_msg = (
                        "I couldn't find a suitable query template for your question."
                    )
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )


if __name__ == "__main__":
    main()
