# Load .env file if it exists
ifneq ("$(wildcard .env)","")
	include .env
	export
endif

# Fallback defaults (can be overridden in .env or via command line)
OLLAMA_HOST ?= localhost
OLLAMA_PORT ?= 11434
OLLAMA_MODEL ?= llama3.2

FUSEKI_HOST ?= localhost
FUSEKI_PORT ?= 3030
FUSEKI_ENDPOINT ?= office

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
fuseki-load:  ## Clear and load all TTL files in fuseki/data into Fuseki
	@echo "Clearing all data from Fuseki /$(FUSEKI_ENDPOINT)..."
	curl -s -X DELETE http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(FUSEKI_ENDPOINT)/data?default || echo "❌ Failed to clear data"
	@echo "Loading TTL files from fuseki/data/..."
	for file in fuseki/data/*.ttl; do \
	  echo "Uploading $$file..."; \
	  curl -s -X POST -H "Content-Type: text/turtle" \
	       --data-binary "@$$file" \
	       http://$(FUSEKI_HOST):$(FUSEKI_PORT)/$(FUSEKI_ENDPOINT)/data?default || exit 1; \
	done
	@echo "All TTL files loaded successfully."

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
