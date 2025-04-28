# Helios UI Acceptance Test Checklist

## Overview
This document provides a formal checklist for acceptance testing of the Helios UI application. These tests are designed to be performed manually to verify that the application meets end-user requirements and functions correctly in realistic usage scenarios.

## Test Environment Setup
- [ ] Clean installation of latest Helios UI
- [ ] Python 3.x with all dependencies installed
- [ ] All Unity simulation builds available
- [ ] Test data prepared

## AT-001: Application Startup Test
**Description:** Verify application starts correctly

**Procedure:**
1. [ ] Launch application via `python main.py`
2. [ ] Verify main window appears with correct title
3. [ ] Confirm all tabs are present (Dashboard, Control, Visualization)
4. [ ] Verify application size and position are appropriate

**Expected Result:** Main window displays correctly with all components visible

**Notes:**
- Application Version: 
- Issues Encountered:
- Test Date:
- Tester:

## AT-002: Simulation Options Test
**Description:** Verify simulation options are correctly displayed

**Procedure:**
1. [ ] Open simulation dropdown on Control tab
2. [ ] Verify all configured simulations are listed
3. [ ] Select each option and verify selection updates correctly
4. [ ] Confirm UI elements update based on selected simulation

**Expected Result:** Options match configuration in MainWindow simulations_config

**Notes:**
- Simulations Listed:
- Issues Encountered:
- Test Date:
- Tester:

## AT-003: Start Simulation Test
**Description:** Verify simulation starts correctly

**Procedure:**
1. [ ] Select "Wildfire" simulation
2. [ ] Click Start button
3. [ ] Verify Unity window launches
4. [ ] Confirm simulation begins running
5. [ ] Verify start command is sent to simulation

**Expected Result:** Simulation launches and runs correctly

**Notes:**
- Startup Time:
- Issues Encountered:
- Test Date:
- Tester:

## AT-004: Pause Simulation Test
**Description:** Verify simulation pauses correctly

**Procedure:**
1. [ ] Start simulation as in AT-003
2. [ ] Allow simulation to run for 30 seconds
3. [ ] Click Pause button
4. [ ] Verify simulation visibly pauses
5. [ ] Confirm pause command is sent to simulation

**Expected Result:** Simulation pauses when button is clicked

**Notes:**
- Pause Response Time:
- Issues Encountered:
- Test Date:
- Tester:

## AT-005: Resume Simulation Test
**Description:** Verify simulation resumes correctly

**Procedure:**
1. [ ] Complete AT-004 Pause Simulation Test
2. [ ] Click Start button again to resume
3. [ ] Verify simulation resumes from paused state
4. [ ] Confirm resume command is sent to simulation

**Expected Result:** Simulation resumes operation from paused state

**Notes:**
- Resume Response Time:
- Issues Encountered:
- Test Date:
- Tester:

## AT-006: Stop Simulation Test
**Description:** Verify simulation stops correctly

**Procedure:**
1. [ ] Start simulation as in AT-003
2. [ ] Allow simulation to run for 30 seconds
3. [ ] Click Stop button
4. [ ] Verify simulation window closes
5. [ ] Confirm stop command is sent
6. [ ] Verify data is saved to CSV file

**Expected Result:** Simulation ends and data is saved

**Notes:**
- Shutdown Time:
- Data Saved Location:
- Issues Encountered:
- Test Date:
- Tester:

## AT-007: Sensor Data Display Test
**Description:** Verify sensor data is displayed correctly

**Procedure:**
1. [ ] Start a simulation
2. [ ] Run for at least 60 seconds
3. [ ] Verify temperature graph updates with incoming data
4. [ ] Verify humidity graph updates with incoming data
5. [ ] Verify battery level indicator updates
6. [ ] Verify position map updates with robot position

**Expected Result:** All data visualizations update in real-time

**Notes:**
- Update Frequency:
- Graph Accuracy:
- Issues Encountered:
- Test Date:
- Tester:

## AT-008: PDF Report Generation Test
**Description:** Verify PDF report generation

**Procedure:**
1. [ ] Run a complete simulation cycle (start and stop)
2. [ ] Click "Generate Report" button
3. [ ] Verify PDF is created with correct filename
4. [ ] Open PDF and verify it contains:
   - [ ] Title and date
   - [ ] Temperature graph
   - [ ] Humidity graph
   - [ ] Mission summary statistics
   - [ ] Robot trajectory map

**Expected Result:** PDF report is generated with all expected content

**Notes:**
- PDF File Location:
- Report Content Quality:
- Issues Encountered:
- Test Date:
- Tester:

## Final Acceptance

The application has passed all acceptance tests and is ready for release.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Lead | | | |
| Development Lead | | | |
| Project Manager | | | | 