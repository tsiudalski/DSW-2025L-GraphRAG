import pytest
import requests
import json
import os
from app.sparql_query_processor import SPARQLQueryProcessor

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
        ollama_host=None  # Disable Ollama for template selection tests
    )

class TestTemplateSelection:
    @pytest.mark.parametrize("test_case", TEST_CASES)
    def test_template_selection(self, processor, test_case):
        """Test if the correct template is selected for each test case."""
        template = processor.find_best_template(test_case['query'])
        assert template is not None, f"Template selection failed for {test_case['id']}"
        assert template.template_name == test_case['expected_template'], \
            f"Wrong template selected for {test_case['id']}. Expected {test_case['expected_template']}, got {template.template_name}" 