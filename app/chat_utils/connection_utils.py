import requests

def test_ollama_connection(ollama_url, ollama_model):
    """Test connection to Ollama service"""
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
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