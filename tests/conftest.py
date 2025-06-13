import pytest
from _pytest.terminal import TerminalReporter
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global counters for test results
template_tests_passed = 0
template_tests_total = 0
param_tests_passed = 0
param_tests_total = 0
sparql_tests_passed = 0
sparql_tests_total = 0

def pytest_report_teststatus(report, config):
    """Track test results."""
    if report.when == "call":  # Only count the actual test call, not setup/teardown
        global template_tests_passed, template_tests_total, param_tests_passed, param_tests_total, sparql_tests_passed, sparql_tests_total
        
        if "TestTemplateSelection" in report.nodeid:
            template_tests_total += 1
            if report.outcome == "passed":
                template_tests_passed += 1
        elif "TestParameterExtraction" in report.nodeid:
            param_tests_total += 1
            if report.outcome == "passed":
                param_tests_passed += 1
        elif "TestSPARQLQueryExecution" in report.nodeid:
            sparql_tests_total += 1
            if report.outcome == "passed":
                sparql_tests_passed += 1

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add accuracy metrics to the terminal summary."""
    if template_tests_total > 0:
        template_accuracy = (template_tests_passed / template_tests_total) * 100
        terminalreporter.write_sep("=", f"Template Selection Accuracy: {template_accuracy:.1f}%")
    
    if param_tests_total > 0:
        param_accuracy = (param_tests_passed / param_tests_total) * 100
        terminalreporter.write_sep("=", f"Parameter Extraction Accuracy: {param_accuracy:.1f}%")
    
    if sparql_tests_total > 0:
        sparql_accuracy = (sparql_tests_passed / sparql_tests_total) * 100
        terminalreporter.write_sep("=", f"SPARQL Query Execution Accuracy: {sparql_accuracy:.1f}%")

def pytest_html_report_title(report):
    """Add accuracy metrics to the report title."""
    global template_tests_passed, template_tests_total, param_tests_passed, param_tests_total, sparql_tests_passed, sparql_tests_total
    
    template_accuracy = (template_tests_passed / template_tests_total * 100) if template_tests_total > 0 else 0
    param_accuracy = (param_tests_passed / param_tests_total * 100) if param_tests_total > 0 else 0
    sparql_accuracy = (sparql_tests_passed / sparql_tests_total * 100) if sparql_tests_total > 0 else 0
    
    embedding_model_name = os.getenv('EMBEDDING_MODEL', 'mixedbread-ai/mxbai-embed-large-v1')
    ollama_model_name = os.getenv('OLLAMA_MODEL', 'llama2')
    
    return f"Test Report - TS: {template_accuracy:.1f}%, PE: {param_accuracy:.1f}%, SQE: {sparql_accuracy:.1f}% - Embeddings: {embedding_model_name}, LLM: {ollama_model_name}"

def pytest_html_results_summary(prefix, summary, postfix):
    """Add accuracy metrics to the results summary."""
    global template_tests_passed, template_tests_total, param_tests_passed, param_tests_total, sparql_tests_passed, sparql_tests_total
    
    template_accuracy = (template_tests_passed / template_tests_total * 100) if template_tests_total > 0 else 0
    param_accuracy = (param_tests_passed / param_tests_total * 100) if param_tests_total > 0 else 0
    sparql_accuracy = (sparql_tests_passed / sparql_tests_total * 100) if sparql_tests_total > 0 else 0

    embedding_model_name = os.getenv('EMBEDDING_MODEL', 'mixedbread-ai/mxbai-embed-large-v1')
    ollama_model_name = os.getenv('OLLAMA_MODEL', 'llama2')
    
    accuracy_section = f"""
    <div class="accuracy-summary">
        <h3>Model Information</h3>
        <ul>
            <li>Embedding Model: <strong>{embedding_model_name}</strong></li>
            <li>LLM (Ollama) Model: <strong>{ollama_model_name}</strong></li>
        </ul>
        <h3>Key Metrics</h3>
        <table>
            <tr>
                <th>Component</th>
                <th>Passed/Total</th>
                <th>Accuracy</th>
            </tr>
            <tr>
                <td>Template Selection</td>
                <td>{template_tests_passed}/{template_tests_total}</td>
                <td>{template_accuracy:.1f}%</td>
            </tr>
            <tr>
                <td>Parameter Extraction</td>
                <td>{param_tests_passed}/{param_tests_total}</td>
                <td>{param_accuracy:.1f}%</td>
            </tr>
            <tr>
                <td>SPARQL Query Execution</td>
                <td>{sparql_tests_passed}/{sparql_tests_total}</td>
                <td>{sparql_accuracy:.1f}%</td>
            </tr>
        </table>
    </div>
    """
    
    prefix.append(accuracy_section) 