# Load .env file if it exists
ifneq ("$(wildcard .env)","")
	include .env
	export
endif

# Fallback defaults (can be overridden in .env or via command line)
MODEL ?= llama2
PORT ?= 11434
FUSEKI_PORT ?= 3030
FUSEKI_ENDPOINT ?= office

help: ## Show this help message
	@echo "Available commands:"; \
	grep -hE '^[a-zA-Z0-9_-]+:.*## ' Makefile | \
	awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Commands
up:  ## Start Fuseki and Ollama containers
	docker-compose up -d

down:  ## Stop and remove containers
	docker-compose down

logs:  ## Show logs from Fuseki and Ollama containers
	docker-compose logs -f

pull-model:  ## Pull model via Ollama (default: llama2)
	docker exec -it ollama ollama pull $(MODEL)

fuseki-load:  ## Clear and load all TTL files in fuseki/data into Fuseki
	@echo "Clearing all data from Fuseki /office..."
	curl -s -X DELETE http://localhost:3030/office/data?default || echo "❌ Failed to clear data"
	@echo "Loading TTL files from fuseki/data/..."
	for file in fuseki/data/*.ttl; do \
	  echo "Uploading $$file..."; \
	  curl -s -X POST -H "Content-Type: text/turtle" \
	       --data-binary "@$$file" \
	       http://localhost:3030/office/data?default || exit 1; \
	done
	@echo "All TTL files loaded successfully."

test-ollama:  ## Send test prompt to Ollama model
	curl -X POST http://localhost:$(PORT)/api/generate \
		-d '{"model": "$(MODEL)", "prompt": "Hello?", "stream": false}'

test-fuseki:   ## Run test query on Fuseki endpoint
	curl -X POST http://localhost:$(FUSEKI_PORT)/$(FUSEKI_ENDPOINT)/sparql \
		--data-urlencode 'query=SELECT * WHERE { ?s ?p ?o } LIMIT 10' \
		-H 'Accept: application/sparql-results+json'

version-check:  ## Print current setup config variables
	@echo "MODEL: $(MODEL)"
	@echo "OLLAMA PORT: $(PORT)"
	@echo "FUSEKI PORT: $(FUSEKI_PORT)"
	@echo "FUSEKI ENDPOINT: $(FUSEKI_ENDPOINT)"
