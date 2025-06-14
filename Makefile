# Load .env file if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif

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

# Main Utils
run-webapp:  ## Start the web application
	@echo "Starting Streamlit UI..."
	poetry run streamlit run --server.fileWatcherType none $(UI_DIR)/app.py

build-template-docs: ## Generate app/data/template_metadata.json for documentation purposes
	poetry run python scripts/generate_template_metadata.py.

# Ollama utils
ollama-pull:  ## Pull model via Ollama
	docker exec -it ollama ollama pull $(OLLAMA_MODEL)

ollama-list: ## List models available via Ollama
	docker exec -it ollama ollama list

# Fuseki operations
fuseki-create:  ## Create a new dataset under DATASET_NAME in Fuseki
	@if [ -z "$(DATASET_NAME)" ]; then \
		echo "Error: DATASET_NAME is required"; \
		exit 1; \
	fi
	@echo "Creating dataset $(DATASET_NAME) in Fuseki..."
	@curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" \
		--data "dbName=$(DATASET_NAME)&dbType=tdb2" \
		http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$$/datasets || echo "Failed to create dataset"

fuseki-delete:  ## Remove the specified dataset DATASET_NAME from Fuseki
	@if [ -z "$(DATASET_NAME)" ]; then \
		echo "Error: DATASET_NAME is required"; \
		exit 1; \
	fi
	@echo "Deleting dataset $(DATASET_NAME) from Fuseki..."
	@curl -s -X DELETE http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$$/datasets/$(DATASET_NAME) || echo "Failed to delete dataset"

fuseki-clear:  ## Clear the data from a specified dataset DATASET_NAME in Fuseki
	@if [ -z "$(DATASET_NAME)" ]; then \
		echo "Error: DATASET_NAME is required"; \
		exit 1; \
	fi
	@echo "Clearing dataset $(DATASET_NAME)..."
	@curl -s -X POST -H "Content-Type: application/sparql-update" \
		--data "CLEAR ALL" \
		http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(DATASET_NAME)/update || echo "Failed to clear dataset"

fuseki-load:  ## Loads a dataset under DATASET_NAME from DATASET_DIR
	@if [ -z "$(DATASET_NAME)" ] || [ -z "$(DATASET_DIR)" ]; then \
		echo "Error: DATASET_NAME and DATASET_DIR are required"; \
		echo "Usage: make fuseki-load DATASET_NAME=<name> DATASET_DIR=<path>"; \
		exit 1; \
	fi
	@echo "Setting up dataset $(DATASET_NAME) with files from $(DATASET_DIR)..."
	@$(MAKE) fuseki-create DATASET_NAME=$(DATASET_NAME)
	@echo "Loading TTL files..."
	@for file in $(DATASET_DIR)/*.ttl; do \
		echo "Uploading $$file..."; \
		curl -s -X POST -H "Content-Type: text/turtle" \
			--data-binary "@$$file" \
			http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(DATASET_NAME)/data || echo "Failed to upload $$file"; \
	done
	@echo "All TTL files loaded successfully."

fuseki-list:  ## Lists datasets loaded to Fuseki
	@echo "Listing all datasets in Fuseki..."
	@curl -s -H "Accept: application/json" http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$$/datasets

# Testing Commands
test:  ## Runs the testcases and generates HTML test report
	pytest tests/test_all.py -v --html=test_report.html --self-contained-html

test-fuseki:  ## Run test query on Fuseki endpoint
	curl -X POST http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(FUSEKI_ENDPOINT)/sparql \
		--data-urlencode 'query=SELECT * WHERE { ?s ?p ?o } LIMIT 10' \
		-H 'Accept: application/sparql-results+json'

test-ollama:  ## Send test prompt to Ollama model
	curl -X POST http://$(OLLAMA_HOST):$(OLLAMA_PORT)/api/generate \
		-d '{"model": "$(OLLAMA_MODEL)", "prompt": "Hello?", "stream": false}'

test-vars:  ## Print current setup config variables
	@echo "OLLAMA HOST:     $(OLLAMA_HOST)"
	@echo "OLLAMA PORT:     $(OLLAMA_PORT)"
	@echo "OLLAMA MODEL:    $(OLLAMA_MODEL)"
	@echo "FUSEKI HOST:     $(FUSEKI_HOST)"
	@echo "FUSEKI PORT:     $(FUSEKI_PORT)"
	@echo "FUSEKI ENDPOINT: $(FUSEKI_ENDPOINT)"
	@echo "DATASET DIR:     $(DATASET_DIR)"
	@echo "DATASET NAME:    $(DATASET_NAME)"
