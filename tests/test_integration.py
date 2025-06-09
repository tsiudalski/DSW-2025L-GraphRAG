import json
import os
import pytest
import re

from app.sparql_query_processor import SPARQLQueryProcessor
from dotenv import load_dotenv


load_dotenv()

def load_test_cases():
    """Loads and parametrizes test cases from the JSON file."""
    path = os.path.join(os.path.dirname(__file__), 'test_cases.json')
    with open(path, 'r') as f:
        data = json.load(f)['test_cases']
    return data

@pytest.fixture(scope="session")
def processor():
    """
    Initializes the SPARQLQueryProcessor for integration testing,
    aligning with the new Makefile and .env structure.
    """
    fuseki_host = os.getenv('FUSEKI_HOST', 'localhost')
    fuseki_port = os.getenv('FUSEKI_PORT', '3030')
    
    dataset_name = os.getenv('DATASET_NAME', 'ds')
    
    ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
    ollama_port = os.getenv('OLLAMA_PORT', '11434')

    fuseki_url = f'http://{fuseki_host}:{fuseki_port}/{dataset_name}/query'
    ollama_url = f'http://{ollama_host}:{ollama_port}'
    
    print(f"\n--- Initializing test processor ---")
    print(f"Targeting Fuseki Dataset: {fuseki_url}")
    print(f"Targeting Ollama Host:    {ollama_url}")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(os.path.join(project_root, 'app'), 'templates')
    if not os.path.exists(templates_dir):
        raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
    
    return SPARQLQueryProcessor(
        templates_dir=templates_dir,
        fuseki_endpoint=fuseki_url,
        ollama_host=ollama_url
    )

# --- Integration Tests ---
@pytest.mark.integration
@pytest.mark.parametrize("test_case", load_test_cases())
def test_query_processing_pipeline(test_case, processor, capsys):
    """
    Runs an integration test by verifying each step of the query processing pipeline.
    This test makes REAL network calls to Ollama and Fuseki.
    """
    query = test_case['query']
    expected_template_id = test_case['expected_template']
    expected_params = test_case['expected_params']
    expected_result = test_case['expected_result']

    # --- Step 1: Find the best template ---
    selected_template = processor.find_best_template(query)
    assert selected_template is not None, "Failed to find any template."
    assert selected_template.template_name == expected_template_id, \
        f"Expected template '{expected_template_id}', but got '{selected_template.template_name}'"
    print(f"\n✅ PASSED [Template Selection]: Correctly selected '{selected_template.template_name}' for query: '{query}'")

    # --- Step 2: Extract parameters from the query ---
    extracted_params = processor.extract_parameters(query, selected_template)
    
    parameterized_template = selected_template.model_construct(**extracted_params)
    errors, missing_params = parameterized_template.validate_fields()
    assert not missing_params, f"Test case has missing parameters: {missing_params}"
    assert not errors, f"Test case has invalid parameters: {errors}"
    validated_params = parameterized_template.model_dump()

    assert validated_params == expected_params, \
        f"Parameter extraction failed. Expected {expected_params}, but got {validated_params}"
    print(f"✅ PASSED [Parameter Extraction]: Correctly extracted parameters: {validated_params}")

    # --- Step 3: Execute the SPARQL query ---
    query_results = processor.execute_query(parameterized_template)

    captured = capsys.readouterr()
    printed_sparql = captured.out.strip()
    
    assert "Generated SPARQL Query:" in printed_sparql, "SPARQL query was not printed"
    
    for key, value in expected_params.items():
        param_value_to_check = str(value).split(':')[-1]
        assert param_value_to_check in printed_sparql, \
            f"Expected parameter value '{param_value_to_check}' not in printed SPARQL query."
    print(f"✅ PASSED [Query Execution]: SPARQL query was correctly generated, populated, and executed.")

    # --- Step 4: Validate the SPARQL query result ---
    assert query_results, "Query returned no results."

    actual_result_binding = query_results[0]['result']['value']

    assert actual_result_binding == expected_result, \
        f"SPARQL result mismatch. Expected '{expected_result}', but got '{actual_result_binding}'."

    print(f"✅ PASSED [SPARQL Result Validation]: The query returned the correct value '{expected_result}'.")