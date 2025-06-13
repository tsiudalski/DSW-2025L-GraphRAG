import pytest
from _pytest.terminal import TerminalReporter

# Global counters for test results
template_tests_passed = 0
template_tests_total = 0
param_tests_passed = 0
param_tests_total = 0

def pytest_report_teststatus(report, config):
    """Track test results."""
    if report.when == "call":  # Only count the actual test call, not setup/teardown
        global template_tests_passed, template_tests_total, param_tests_passed, param_tests_total
        
        if "TestTemplateSelection" in report.nodeid:
            template_tests_total += 1
            if report.outcome == "passed":
                template_tests_passed += 1
        elif "TestParameterExtraction" in report.nodeid:
            param_tests_total += 1
            if report.outcome == "passed":
                param_tests_passed += 1

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add accuracy metrics to the terminal summary."""
    if template_tests_total > 0:
        template_accuracy = (template_tests_passed / template_tests_total) * 100
        terminalreporter.write_sep("=", f"Template Selection Accuracy: {template_accuracy:.1f}%")
    
    if param_tests_total > 0:
        param_accuracy = (param_tests_passed / param_tests_total) * 100
        terminalreporter.write_sep("=", f"Parameter Extraction Accuracy: {param_accuracy:.1f}%")

def pytest_html_report_title(report):
    """Add accuracy metrics to the report title."""
    global template_tests_passed, template_tests_total, param_tests_passed, param_tests_total
    
    template_accuracy = (template_tests_passed / template_tests_total * 100) if template_tests_total > 0 else 0
    param_accuracy = (param_tests_passed / param_tests_total * 100) if param_tests_total > 0 else 0
    
    return f"Test Report - Template Selection: {template_accuracy:.1f}%, Parameter Extraction: {param_accuracy:.1f}%"

def pytest_html_results_summary(prefix, summary, postfix):
    """Add accuracy metrics to the results summary."""
    global template_tests_passed, template_tests_total, param_tests_passed, param_tests_total
    
    template_accuracy = (template_tests_passed / template_tests_total * 100) if template_tests_total > 0 else 0
    param_accuracy = (param_tests_passed / param_tests_total * 100) if param_tests_total > 0 else 0
    
    accuracy_section = f"""
    <div class="accuracy-summary">
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
        </table>
    </div>
    """
    
    prefix.append(accuracy_section) 