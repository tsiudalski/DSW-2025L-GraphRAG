# DSW-2025L-GraphRAG

## Example schema:
![Example Samsung device schema](https://github.com/user-attachments/assets/6fe595b9-ac20-4c4b-9789-87102444e6d3)


## (Possibly) useful links:
- [LLM-based SPARQL Query Generation from Natural Language over Federated Knowledge Graphs](https://arxiv.org/html/2410.06062v1)
- [Retrieval Augmented Generation (RAG) with Knowledge Graph using SPARQL](https://github.com/aws-samples/rag-with-knowledge-graph-using-sparql/tree/main)

## Questions related to templates:
- template1: What is the average temperature measured by a specific device within a given time range, along with the device type and measurement unit?
- template2: How many devices of each type are present on a specific floor?

## 🧑‍💻 Development Guide

This project supports two development workflows:

---

#### Prerequisites

- [Docker](https://www.docker.com/)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### 1. (Recommended) Dev Container (VS Code + Docker)

The preferred approach uses a **VS Code Dev Container**, providing:
- Preconfigured Python + Poetry + Jupyter
- Networked access to Fuseki and Ollama
- Easy environment reproducibility

**Steps**

1. Clone this repository.
2. Open the folder in VS Code.
3. Press `Ctrl+Shift+P → Dev Containers: Reopen in Container`.

Once the environment is built and open, you may develop code as you like.
To test connection with Apache Fuseki and Ollama use predefined make commands.
To see the list of all make commands use `make help`.

### 2. Without Dev Container

**Steps**

1. Clone this repository.
2. Open the folder in VS Code.
3. Use `make up` to build the services. You may need to use additional make commands, and other manual commands to develop new code in this setup.


TODO:
[] mini graph for demo


# How to add a new dataset / graph?

Prerequisites: 
- have an active environment with the dependencies
- have the docker container hosting Fuseki runnning (`make up`)

To create a new empty dataset run:
`make fuseki-create-dataset DATASET_NAME=<your-dataset-name>"

To add a new dataset and populate it with .ttl files from a specified directory, run:
`make fuseki-load-dataset DATASET_NAME=<your-dataset-name> DATASET_DIR=<dir-with-ttl-files>"