# Helios Test Procedures Document

## 1. Overview

This document outlines the testing procedures for the Helios UI application, covering unit testing, integration testing, and acceptance testing. The document provides a structured approach to verifying that the application meets all functional requirements and quality standards.

## 2. Test Environment

### 2.1 Requirements
- Python 3.x
- PyQt5 >=5.15.0
- pytest ==7.4.0
- pytest-qt ==4.2.0
- pytest-mock ==3.11.1
- coverage ==7.3.2

### 2.2 Test Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Test Directory Structure
```
Helios/tests/
├── unit/           # Unit tests for individual components
├── integration/    # Tests for component interactions
│   └── test_simulation_lifecycle.py
├── acceptance/     # End-to-end functionality tests
├── test_helios.py  # Core application logic tests
├── test_socket_communication.py  # Network tests
├── test_ui.py      # UI component tests
├── test_main_coverage.py  # Coverage verification tests
├── conftest.py     # Test fixtures and configuration
├── run_tests.bat   # Script to run main tests
└── run_with_coverage.bat  # Script to run tests with coverage reporting
```

## 3. Unit Testing

### 3.1 Purpose
Unit tests verify that individual components function correctly in isolation.

### 3.2 Test Cases

#### 3.2.1 Simulation Configuration Tests
| Test ID | Description | Input | Expected Output | Pass/Fail Criteria |
|---------|-------------|-------|----------------|-------------------|
| UT-001  | Verify simulation configuration structure | Initialize MainWindow | Simulation config with required fields | All required keys exist in config |
| UT-002  | Verify wildfire configuration | Access wildfire config | Configuration has valid exe_path, title, hwnd_title | All fields properly configured |

#### 3.2.2 Data Handling Tests
| Test ID | Description | Input | Expected Output | Pass/Fail Criteria |
|---------|-------------|-------|----------------|-------------------|
| UT-003  | Test CSV data insertion | Robot type, world type, disaster type, start/end times | Data correctly written to CSV | Data matches expected format in CSV |
| UT-004  | Test resolution time calculation | Start/end time strings | Correct time difference in seconds | Calculated value matches expected |

#### 3.2.3 UI Component Tests
| Test ID | Description | Input | Expected Output | Pass/Fail Criteria |
|---------|-------------|-------|----------------|-------------------|
| UT-005  | Test UI component initialization | Create UI components | Components initialized with correct properties | Properties match expected values |
| UT-006  | Test UI event handling | Trigger UI events | Event handlers called with correct parameters | Event handlers respond correctly |

### 3.3 Test Execution Procedure
```bash
cd Helios_UI
pytest -v Helios/tests/unit/
```

## 4. Integration Testing

### 4.1 Purpose
Integration tests verify that different components work together correctly.

### 4.2 Test Cases

#### 4.2.1 Simulation Lifecycle Tests
| Test ID | Description | Input | Expected Output | Pass/Fail Criteria |
|---------|-------------|-------|----------------|-------------------|
| IT-001  | Test full simulation lifecycle | Start, pause, stop simulation | Correct state transitions and function calls | All expected methods called in sequence |
| IT-002  | Test UI and simulation interaction | UI input for simulation control | Correct commands sent to simulation | Commands match expected protocol |

#### 4.2.2 Socket Communication Tests
| Test ID | Description | Input | Expected Output | Pass/Fail Criteria |
|---------|-------------|-------|----------------|-------------------|
| IT-003  | Test socket initialization | Start application | Socket server starts correctly | Socket initialized in listening state |
| IT-004  | Test command transmission | Send commands through socket | Commands received by simulation | Correct command format received |
| IT-005  | Test data reception | Send data from simulation | Data correctly processed by application | Application state updated correctly |

### 4.3 Test Execution Procedure
```bash
cd Helios_UI
pytest -v Helios/tests/integration/
# Or run specific integration tests:
pytest -v Helios/tests/integration/test_simulation_lifecycle.py
```

## 5. Acceptance Testing

### 5.1 Purpose
Acceptance tests verify that the application meets end-user requirements and functions correctly in realistic usage scenarios.

### 5.2 Test Cases

#### 5.2.1 Application Startup Tests
| Test ID | Description | Procedure | Expected Result | Pass/Fail Criteria |
|---------|-------------|-----------|----------------|-------------------|
| AT-001  | Verify application starts correctly | Launch application via main.py | Application window appears with correct layout | Main window displays correctly |
| AT-002  | Verify simulation options | Open simulation dropdown | All configured simulations shown | Options match configuration |

#### 5.2.2 Simulation Control Tests
| Test ID | Description | Procedure | Expected Result | Pass/Fail Criteria |
|---------|-------------|-----------|----------------|-------------------|
| AT-003  | Start simulation test | Select simulation and click start | Simulation launches and receives start command | Simulation visible and running |
| AT-004  | Pause simulation test | Click pause during running simulation | Simulation pauses | Simulation visibly paused |
| AT-005  | Resume simulation test | Click resume after pausing | Simulation continues | Simulation resumes operation |
| AT-006  | Stop simulation test | Click stop during running simulation | Simulation ends and data saved | Simulation closes and data in CSV |

#### 5.2.3 Data Visualization Tests
| Test ID | Description | Procedure | Expected Result | Pass/Fail Criteria |
|---------|-------------|-----------|----------------|-------------------|
| AT-007  | Verify sensor data display | Run simulation sending sensor data | Data displayed in appropriate graphs | Graphs update with incoming data |
| AT-008  | Test PDF report generation | Generate PDF report | Report created with correct data | PDF contains expected graphs and data |

### 5.3 Test Execution Procedure
```bash
cd Helios_UI
pytest -v Helios/tests/acceptance/
```

## 6. Test Coverage

### 6.1 Coverage Goals
- Unit tests: 90% code coverage
- Integration tests: 80% integration coverage
- Acceptance tests: 100% feature coverage

### 6.2 Coverage Measurement
```bash
cd Helios_UI
# Run coverage using the provided batch file
.\run_with_coverage.bat

# Or run manually with specific options
python -m pytest Helios/tests/ --cov=Helios --cov-report=html --cov-report=term --cov-config=.coveragerc
```

### 6.3 Coverage Configuration
Coverage configuration is defined in `.coveragerc` and excludes test files, caches, and other non-application code.

## 7. Bug Tracking and Reporting

### 7.1 Bug Report Format
- Bug ID
- Description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Severity (Critical, High, Medium, Low)
- Status (New, In Progress, Fixed, Closed)

### 7.2 Bug Tracking Process
1. Identify bug during testing
2. Document using bug report format
3. Assign to developer
4. Fix and verify
5. Close bug report

## 8. Regression Testing

### 8.1 Purpose
Ensure that new changes don't break existing functionality.

### 8.2 Regression Test Suite
All unit tests, integration tests, and critical acceptance tests should be run as part of regression testing.

### 8.3 Execution Frequency
Regression tests should be run:
- After any significant code changes
- Before releasing new versions
- After fixing critical bugs

### 8.4 Regression Test Procedure
```bash
cd Helios_UI
# Run all tests
python -m pytest

# Or run with coverage to ensure regression hasn't affected test coverage
.\run_with_coverage.bat
```

## 9. Conclusion and Sign-off

### 9.1 Test Result Summary
(To be filled after test execution)

### 9.2 Recommendations
(To be filled after test execution)

### 9.3 Approvals
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Lead | | | |
| Development Lead | | | |
| Project Manager | | | | 