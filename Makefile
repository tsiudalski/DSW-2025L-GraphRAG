# Load .env file if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Environment variables are now defined in .env file
# Required variables:
# OLLAMA_HOST - Ollama server hostname
# OLLAMA_PORT - Ollama server port
# OLLAMA_MODEL - Ollama model name
# FUSEKI_HOST - Fuseki server hostname
# FUSEKI_PORT - Fuseki server port
# FUSEKI_ENDPOINT - Fuseki endpoint name
# DATASET_DIR - Directory containing TTL files
# DATASET_NAME - Name of the Fuseki dataset
# UI_DIR - Directory containing the Streamlit UI

help: ## Show this help message
	@echo "Available commands:"; \
	grep -hE '^[a-zA-Z0-9_-]+:.*## ' Makefile | \
	awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Container management
up:  ## Start Fuseki and Ollama containers
	docker-compose up -d

down:  ## Stop and remove containers
	docker-compose down

logs:  ## Show logs from Fuseki and Ollama containers
	docker-compose logs -f

pull-model:  ## Pull model via Ollama (default: llama2)
	docker exec -it ollama ollama pull $(OLLAMA_MODEL)

# Fuseki operations
fuseki-create-dataset:
	@if [ -z "$(DATASET_NAME)" ]; then \
		echo "Error: DATASET_NAME is required"; \
		exit 1; \
	fi
	@echo "Creating dataset $(DATASET_NAME) in Fuseki..."
	@curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" \
		--data "dbName=$(DATASET_NAME)&dbType=tdb2" \
		http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$$/datasets || echo "Failed to create dataset"

fuseki-delete-dataset:
	@if [ -z "$(DATASET_NAME)" ]; then \
		echo "Error: DATASET_NAME is required"; \
		exit 1; \
	fi
	@echo "Deleting dataset $(DATASET_NAME) from Fuseki..."
	@curl -s -X DELETE http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$$/datasets/$(DATASET_NAME) || echo "Failed to delete dataset"

fuseki-clear-dataset:
	@if [ -z "$(DATASET_NAME)" ]; then \
		echo "Error: DATASET_NAME is required"; \
		exit 1; \
	fi
	@echo "Clearing dataset $(DATASET_NAME)..."
	@curl -s -X POST -H "Content-Type: application/sparql-update" \
		--data "CLEAR ALL" \
		http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(DATASET_NAME)/update || echo "Failed to clear dataset"

fuseki-load-dataset:
	@if [ -z "$(DATASET_NAME)" ] || [ -z "$(DATASET_DIR)" ]; then \
		echo "Error: DATASET_NAME and DATASET_DIR are required"; \
		echo "Usage: make fuseki-load-dataset DATASET_NAME=<name> DATASET_DIR=<path>"; \
		exit 1; \
	fi
	@echo "Setting up dataset $(DATASET_NAME) with files from $(DATASET_DIR)..."
	@$(MAKE) fuseki-create-dataset DATASET_NAME=$(DATASET_NAME)
	@echo "Loading TTL files..."
	@for file in $(DATASET_DIR)/*.ttl; do \
		echo "Uploading $$file..."; \
		curl -s -X POST -H "Content-Type: text/turtle" \
			--data-binary "@$$file" \
			http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(DATASET_NAME)/data || echo "Failed to upload $$file"; \
	done
	@echo "All TTL files loaded successfully."

fuseki-list-datasets:
	@echo "Listing all datasets in Fuseki..."
	@curl -s -H "Accept: application/json" http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$$/datasets

test-fuseki:  ## Run test query on Fuseki endpoint
	curl -X POST http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(FUSEKI_ENDPOINT)/sparql \
		--data-urlencode 'query=SELECT * WHERE { ?s ?p ?o } LIMIT 10' \
		-H 'Accept: application/sparql-results+json'

test-ollama:  ## Send test prompt to Ollama model
	curl -X POST http://$(OLLAMA_HOST):$(OLLAMA_PORT)/api/generate \
		-d '{"model": "$(OLLAMA_MODEL)", "prompt": "Hello?", "stream": false}'

version-check:  ## Print current setup config variables
	@echo "OLLAMA HOST:     $(OLLAMA_HOST)"
	@echo "OLLAMA PORT:     $(OLLAMA_PORT)"
	@echo "OLLAMA MODEL:    $(OLLAMA_MODEL)"
	@echo "FUSEKI HOST:     $(FUSEKI_HOST)"
	@echo "FUSEKI PORT:     $(FUSEKI_PORT)"
	@echo "FUSEKI ENDPOINT: $(FUSEKI_ENDPOINT)"
	@echo "DATASET DIR:     $(DATASET_DIR)"
	@echo "DATASET NAME:    $(DATASET_NAME)"

run-webapp:  ## Run the Streamlit UI
	@echo "Starting Streamlit UI..."
	poetry run streamlit run $(UI_DIR)/app.py
