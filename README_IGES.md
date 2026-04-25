# SmartBugs - IGES Extension Project

This repository contains an academic extension of the SmartBugs framework, developed for the course:

**Ingegneria, Gestione ed Evoluzione del Software (IGES)**

---

## Project Goal

Extend SmartBugs with an **intelligent tool-selection mechanism** based on:
- Feature extraction from smart contracts
- Machine learning models for tool prediction

Objective:
Automatically select the most suitable analysis tools, improving usability and effectiveness.

---

## Current Status

The project is currently in the **analysis and design phase**.

Completed activities:
- Reverse engineering of SmartBugs architecture
- Identification of core modules and responsibilities
- Creation of:
  - Package diagram
  - Class diagram
  - Sequence diagrams (current and proposed)
  - Dependency matrix
- Definition of Change Requests (CRs)
- Impact analysis (SIS, CIS)

➡ Implementation is ongoing.

---

## Proposed Workflow

1. Extract features (SCsVulLyzer)
2. Select relevant features
3. Execute ML models
4. Predict tools
5. Aggregate and filter results
6. Execute SmartBugs with selected tools

Design goals:
- Modular
- Non-intrusive
- Backward compatible

---

## Change Requests

### CR_1 - Feature Extraction
- Integrate SCsVulLyzer
- Extract structured features

### CR_2 - ML Tool Selection
- Load pre-trained models
- Predict and aggregate tools

### CR_3 - Workflow Integration
- Extend orchestrator
- Add intelligent execution mode

---

## Architecture Insights

- `sb.smartbugs` is the central orchestrator
- System is modular and layered
- Execution is isolated via Docker
- Extension is feasible at orchestration level

---

## Scope of Modifications

- No changes to core execution pipeline
- New components added modularly
- Limited impact on existing modules

---

## Repository Structure

- `sb/` → Core SmartBugs modules  
- `tests/` → Test suite  
- `external/SCsVulLyzer/` → Feature extraction  
- `models/ML_models/` → Pre-trained models  
- `docs/` → Report and diagrams  

---

## Testing Strategy (Planned)

- Unit tests for new components
- Integration tests for full workflow
- Regression testing on existing features

---

## Documentation

Full details (analysis, changes, impact, testing) are available in the project report.

---

## Notes

This is an academic project and not part of the official SmartBugs repository.