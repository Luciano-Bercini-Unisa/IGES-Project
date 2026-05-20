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

## Repository Structure

- `sb/` → Core SmartBugs modules  
- `tests/` → Test suite  
- `external/SCsVulLyzer/` → Feature extraction  
- `models/ML_models/` → Pre-trained models  
- `docs/` → Report and diagrams  

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

## Example run with smart settings
- python -m sb --smart-select -f samples/0.8.24/ERC20.sol

---

## Limitations

The feature extraction module supports only Solidity contracts (.sol) and not compiled ones (.hex).
All 8 machine learning models sometimes predict "nessun_tool" for certain smart contracts (e.g. Government.sol).

---

## Documentation

Full details (analysis, changes, impact, testing) are available in the project report.

---

## Additional Dependencies

The intelligent tool-selection extension adds the following Python dependencies:

- pandas
- joblib
- scikit-learn==1.6.1

The scikit-learn version is pinned because the provided pre-trained `.joblib` models were serialized with scikit-learn 1.6.1.

---

## Notes

This is an academic project and not part of the official SmartBugs repository.
