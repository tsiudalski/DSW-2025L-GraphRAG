import requests
import json
import numpy as np
import os
import sys
from dotenv import load_dotenv
from sparql_query_processor import SPARQLQueryProcessor
from chat_utils.connection_utils import (
    test_fuseki_connection,
    test_ollama_connection
)

load_dotenv()

FUSEKI_HOST = os.getenv('FUSEKI_HOST', 'localhost')
FUSEKI_PORT = os.getenv('FUSEKI_PORT', '3030')
FUSEKI_ENDPOINT = os.getenv('FUSEKI_ENDPOINT', 'ds')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')

if __name__ == "__main__":

    app_dir = os.path.dirname(os.path.abspath(__file__))
    fuseki_url = f'http://{FUSEKI_HOST}:{FUSEKI_PORT}/{FUSEKI_ENDPOINT}/query'
    ollama_url = f'http://{OLLAMA_HOST}:{OLLAMA_PORT}'

    # if not test_fuseki_connection(fuseki_url):
    #     print("Exiting due to Fuseki connection failure")
    #     sys.exit(1)
    
    # if not test_ollama_connection(ollama_url):
    #     print("Exiting due to Ollama connection failure")
    #     sys.exit(1)

    processor = SPARQLQueryProcessor(
        templates_dir=os.path.join(app_dir, 'templates'),
        fuseki_endpoint=fuseki_url,
        ollama_host=ollama_url
    )

    user_input = ""

    while True:
        new_user_input = input(">>> ")
        if new_user_input.lower() == "exit":
            break

        user_input = user_input + new_user_input
        status, response = processor.process_query(user_input)
        if status == "RESET":  
            user_input = ""
        elif status == "CONTINUE":
            user_input = user_input + " UPDATE:"
        else:
            print("Internal Error :(")
            break

