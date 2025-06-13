import json
import os
import pytest
import requests
from app.sparql_query_processor import SPARQLQueryProcessor

# Load test cases
with open(os.path.join(os.path.dirname(__file__), 'test_cases.json')) as f:
    TEST_CASES = json.load(f)['test_cases']

# Test configuration
FUSEKI_ENDPOINT = "http://localhost:3030/demo7floor/sparql"
OLLAMA_HOST = "http://localhost:11434"
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates')

@pytest.fixture
def processor():
    """Create a SPARQLQueryProcessor instance for testing."""
    return SPARQLQueryProcessor(
        templates_dir=TEMPLATES_DIR,
        fuseki_endpoint=FUSEKI_ENDPOINT,
        ollama_host=OLLAMA_HOST
    )

# Test Suite 1: Template Selection Tests
class TestTemplateSelection:  # Note: this is deterministic => no need for re-run
    @pytest.mark.parametrize("test_case", TEST_CASES)
    def test_template_selection(self, processor, test_case):
        """Test if the correct template is selected for each test case."""
        template = processor.find_best_template(test_case['query'])
        assert template is not None, f"Template selection failed for {test_case['id']}"
        assert template.template_name == test_case['expected_template'], \
            f"Wrong template selected for {test_case['id']}. Expected {test_case['expected_template']}, got {template.template_name}"

# Test Suite 2: Parameter Extraction Tests
class TestParameterExtraction:
    @pytest.mark.parametrize("test_case", TEST_CASES)
    def test_parameter_extraction(self, processor, test_case):
        """Test if parameters are correctly extracted and validated."""
        template = processor.find_best_template(test_case['query'])
        parameters = processor.extract_parameters(test_case['query'], template)
        
        # Create and validate template with parameters
        parameterized_template, errors, missing = template.create_and_validate(parameters)
        
        # Check for validation errors
        assert not errors, f"Validation errors for {test_case['id']}: {errors}"
        assert not missing, f"Missing parameters for {test_case['id']}: {missing}"
        
        # Compare with expected parameters
        for param_name, expected_value in test_case['expected_params'].items():
            actual_value = getattr(parameterized_template, param_name)
            assert str(actual_value) == str(expected_value), \
                f"Wrong value for parameter {param_name} in {test_case['id']}. Expected {expected_value}, got {actual_value}"

# Test Suite 3: SPARQL Query Execution Tests
class TestQueryExecution:
    @pytest.mark.parametrize("test_case", TEST_CASES)
    def test_query_execution(self, processor, test_case):
        """Test if SPARQL query execution returns expected results."""
        template = processor.find_best_template(test_case['query'])
        parameters = test_case['expected_params']  # Use expected parameters directly
        
        # Create and validate template with parameters
        parameterized_template, errors, missing = template.create_and_validate(parameters)
        assert parameterized_template is not None, \
            f"Template validation failed for {test_case['id']}: {errors}"
        
        # Execute query
        results = processor.execute_query(parameterized_template)
        assert results is not None, f"Query execution failed for {test_case['id']}"
        
        # Extract the result value (assuming single result)
        if results:
            result_value = results[0].get('value', {}).get('value')
            assert str(result_value) == str(test_case['expected_result']), \
                f"Wrong result for {test_case['id']}. Expected {test_case['expected_result']}, got {result_value}"
        else:
            pytest.fail(f"No results returned for {test_case['id']}") 