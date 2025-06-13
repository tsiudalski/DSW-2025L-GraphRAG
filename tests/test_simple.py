import pytest
import requests
import json
import os
from app.sparql_query_processor import SPARQLQueryProcessor
from app.models import TEMPLATE_REGISTRY

# Global counters for test results
template_tests_passed = 0
template_tests_total = 0
param_tests_passed = 0
param_tests_total = 0

def test_services():
    """Test if services are running."""
    # Check Fuseki
    try:
        response = requests.get("http://localhost:3030/demo7floor/")
        print(f"Fuseki status: {response.status_code}")
        assert response.status_code in [200, 400], "Fuseki service is not responding correctly"
    except requests.exceptions.ConnectionError:
        pytest.fail("Fuseki service is not running. Please start it with 'docker-compose up -d fuseki'")

    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags")
        print(f"Ollama status: {response.status_code}")
        assert response.status_code == 200, "Ollama service is not responding correctly"
    except requests.exceptions.ConnectionError:
        pytest.fail("Ollama service is not running. Please start it with 'docker-compose up -d ollama'")

def test_basic_math():
    """A very basic test to ensure pytest is working."""
    assert 1 + 1 == 2, "Basic math is broken"

# Load test cases
with open(os.path.join(os.path.dirname(__file__), 'test_cases.json')) as f:
    TEST_CASES = json.load(f)['test_cases']

@pytest.fixture
def processor():
    """Create a SPARQLQueryProcessor instance for testing."""
    return SPARQLQueryProcessor(
        templates_dir="app/templates",
        fuseki_endpoint="http://localhost:3030/demo7floor/sparql",
        ollama_host="http://localhost:11434"  # Enable Ollama for parameter extraction
    )

class TestTemplateSelection:
    @pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc['id'] for tc in TEST_CASES])
    def test_template_selection(self, processor, test_case):
        """Test if the correct template is selected for each test case."""
        global template_tests_passed, template_tests_total
        
        try:
            template = processor.find_best_template(test_case['query'])
            assert template is not None, f"Template selection failed for {test_case['id']}"
            assert template.template_name == test_case['expected_template'], \
                f"Wrong template selected for {test_case['id']}. Expected {test_case['expected_template']}, got {template.template_name}"
            template_tests_passed += 1
        except AssertionError:
            raise
        finally:
            template_tests_total += 1
            print(f"✓ Template Selection: {test_case['id']}" if template_tests_passed == template_tests_total else f"✗ Template Selection: {test_case['id']}")

    def teardown_class(self):
        """Print summary after all template selection tests are done."""
        if template_tests_total > 0:
            accuracy = (template_tests_passed / template_tests_total) * 100
            print("\nTemplate Selection Summary:")
            print(f"Passed: {template_tests_passed}/{template_tests_total} tests")
            print(f"Accuracy: {accuracy:.1f}%")

class TestParameterExtraction:
    @pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc['id'] for tc in TEST_CASES])
    def test_parameter_extraction(self, processor, test_case):
        """Test if parameters are correctly extracted and validated."""
        global param_tests_passed, param_tests_total
        
        try:
            # Get the expected template directly from registry
            template = TEMPLATE_REGISTRY[test_case['expected_template']]
            assert template is not None, f"Template not found: {test_case['expected_template']}"
            
            # Extract parameters
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
            
            param_tests_passed += 1
        except AssertionError:
            raise
        finally:
            param_tests_total += 1
            print(f"✓ Parameter Extraction: {test_case['id']}" if param_tests_passed == param_tests_total else f"✗ Parameter Extraction: {test_case['id']}")

    def teardown_class(self):
        """Print summary after all parameter extraction tests are done."""
        if param_tests_total > 0:
            accuracy = (param_tests_passed / param_tests_total) * 100
            print("\nParameter Extraction Summary:")
            print(f"Passed: {param_tests_passed}/{param_tests_total} tests")
            print(f"Accuracy: {accuracy:.1f}%") 