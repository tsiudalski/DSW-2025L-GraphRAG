# GraphRAG-Powered QA Chat for OfficeGraph

**OfficeGraph QA Chat** is a conversational question-answering (QA) assistant designed for the [OfficeGraph](https://github.com/RoderickvanderWeerdt/OfficeGraph/tree/main) — an IoT knowledge graph representing real-world sensor data and device metadata from office environments.

The system allows users to query RDF data using natural language by combining sentence embedding-based template selection, SPARQL query execution, and large language model (LLM)-powered natural language generation. While tailored to the structure and semantics of OfficeGraph, the architecture is modular and can be adapted to other RDF-based knowledge graphs in different domains.

> **Note:** This project was developed as part of the *Data Science Workshop* course in the MEng Data Science programme at Warsaw University of Technology (WUT).

## Dataset
This system is built around the **OfficeGraph** dataset — an RDF knowledge graph representing IoT sensor data from an office building. The graph captures both static metadata (e.g., device types, locations) and dynamic measurements (e.g., temperature readings) over time.

**Data Summary**
- **Source**: Real-world IoT deployment in an office building
- **Devices**: 444 total
- **Time Range**: from March 1, 2022 to January 31, 2023
- **Measurements**: 11 different types (e.g., temperature, CO₂, humidity)
- **Scale**: ~90 million RDF triples
- **Demo Scope**: Subgraph for devices located on the 7th floor (~1.8M triples)

**Example Schema**
![Example Samsung device schema](https://github.com/user-attachments/assets/6fe595b9-ac20-4c4b-9789-87102444e6d3)

## Setup Guide

### Prerequisites

Make sure the following **tools** are installed on your system:
- [Docker](https://www.docker.com/) - for containerization
- [Docker Compose](https://docs.docker.com/compose/install/) - for managing multi-container setups (v2+)
- [Make](https://www.gnu.org/software/make/) - used to run common project commands (`make up`, `make run-webapp`, etc.)
- [Python 3.11+](https://www.python.org/downloads/) - for running the app and scripts
- [Poetry](https://python-poetry.org/docs/#installation) - for managing dependencies
- [Visual Studio Code](https://code.visualstudio.com/) - recommended IDE with support for Python and Docker

Make sure you have enough **disc space** for the following:
- LLM Model (by default `mistral:instruct` via Ollama): ~4.1GB
- Embedding model (by defualt `nomic-ai/nomic-embed-text-v1.5`): ~900MB
- Demo subset of OfficeGraph dataset (7th floor only): ~1.8 triples (~ 4MB)
- Full OfficeGraph dataset: ~90M triples ~100GB+ (refer to [dataset repository]((https://github.com/RoderickvanderWeerdt/OfficeGraph/tree/main) ))


### Quickstart
> **Note**: Before running the steps below, ensure Docker is running.

1. Clone the repository and launch the services:
```bash
git clone https://github.com/<your-org>/OfficeGraph-QA-Chat.git  # Clones this repository
cd OfficeGraph-QA-Chat  # Enters project root
make up            # Starts Fuseki and Ollama containers
```
2. Pull the Ollama model
```bash
make pull-model    # Pulls the default LLM model (set in .env)
```
3. Create a new dataset eg. `demo7floor` and load it with triples from files in specified directory.

- Unzip the attached `floor_7_files.zip` file into a directory of choice `DATASET_DIR` 
- Next, create and load it to the system with custom make command:
   ```bash
   make fuseki-load-dataset DATASET_NAME=demo7floor DATASET_DIR=DATASET_DIR
   ```
   > **Note**: DATASET_DIR should include .ttl files to be loaded to the dataset DATASET_NAME

- Verify that the dataset was created
   ```bash
   make fuseki-list-datasets
   ```
   > **Note**: For more fine control of the datasets use other available make commands. Run `make help` for reference.

4. Check if all the required services are working properly:
- Check Apache Fuseki service:
   ```bash
   make test-fuseki
   ```
   > **Note**: You should see a JSON object as output.
- Check Ollama service:
   ```bash
   make test-ollama
   ```
   > **Note**: You should receive a JSON object with model response to query "Hello".

5. Launch the web application:
```bash
make run-webapp
```
Follow the URLs printed in terminal to open the app in the web browser.

> **Note**: In case this command throws an error, you may need to run `poetry install` to install the required dependencies and `poetry shell` to activate poetry environment 

**Closing the app**
After finishing using the app, to free the resources, run `make down`.

**Customization**
If you want to use a smaller ollama model, embeddings model, endpoints, or ports, you may change them in `.env` file. Note that before using new LLM, you have to pull it first.

## Usage

### Interface and Settings
If you run the web application you will see the inferface with some settings on the left panel and chat on the right.
In the left panel, you may choose:
- the dataset you want to query (eg. `demo7floor`)
- whether the chat should show SPARQL Query during answering
   - whether to show prefix declarations in the SPARQL Query if enabled
- whether to view the output table from Apache Fuseki (recommended for multi-row queries)
> **Note**: Currently the system supports mostly the aggregated single-answer queries, and only a single query that is multi-row 
- to clear the chat history with the trash icon button

### Example Queries

The system supports various types of queries, including:
- *What is the average temperature measured by a specific device within a given time range?*
- *How many devices of each type are present on a specific floor?*
- *What was the last reported CO2 level from a specific device?*
- *How many rooms does a specific floor have?*

You can view the generated SPARQL query (if such option is checked) and response in the chat area on the right of the interface.

> **Note**: To see the full list of supported queries, you may inspect `data/template_metadata.json` which is a file describing each supported query template, and its parameters. You may also inspect `tests/test_cases.json` to see different formulations of questions that the system supports.


## Testing
To run tests, run `make tests`.

> **Note**: In case this command throws an error, you may need to run `poetry install` to install the required dependencies and `poetry shell` to activate poetry environment 

The tests will run, and a new `test_report.html` will appear after the process finishes, stating the number and percentage of tests passed at each stage: template selection, parameter extraction, query execution.

The tests are based on `tests/test_cases.json` file, which can be easily modified and updated with new test cases if needed.

## Useful Resources
- [LLM-based SPARQL Query Generation from Natural Language over Federated Knowledge Graphs](https://arxiv.org/html/2410.06062v1)
- [Retrieval Augmented Generation (RAG) with Knowledge Graph using SPARQL](https://github.com/aws-samples/rag-with-knowledge-graph-using-sparql/tree/main)
