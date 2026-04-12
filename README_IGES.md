\# SmartBugs - IGES Extension Project



This repository contains an academic extension of the SmartBugs framework, developed for the course:



\*\*Progetti di Ingegneria, Gestione ed Evoluzione del Software (IGES)\*\*



\## 📌 Project Goal



The goal of this project is to evolve SmartBugs by introducing an \*\*intelligent tool-selection mechanism\*\* based on:



\- Feature extraction from smart contracts

\- Machine learning models for tool prediction



The objective is to automatically select the most appropriate analysis tools for a given contract, improving both usability and effectiveness.



\---



\## 🔍 Current Status



The project is currently in the \*\*analysis and design phase\*\*.



The following activities have been completed:



\- Reverse engineering of the SmartBugs architecture

\- Identification of core modules and responsibilities

\- Construction of:

&#x20; - Package diagram

&#x20; - Class diagram

&#x20; - Sequence diagrams (current and proposed workflows)

&#x20; - Dependency matrix

\- Definition of Change Requests (CRs)

\- Impact analysis (SIS, CIS)



⚠️ The implementation of the proposed changes is ongoing.



\---



\## 🧠 Proposed Extension



The extension introduces a new workflow:



1\. Extract features from the smart contract (SCsVulLyzer)

2\. Select relevant features

3\. Execute multiple ML models

4\. Predict suitable tools

5\. Aggregate and filter predictions

6\. Execute SmartBugs with selected tools



This workflow is designed to be:



\- Modular

\- Non-intrusive

\- Backward compatible



\---



\## 🔧 Change Requests Overview



The evolution is structured into three main Change Requests:



\### CR\_1 - Feature Extraction Integration

\- Integration of SCsVulLyzer

\- Extraction of structured features from contracts



\### CR\_2 - Machine Learning-Based Tool Selection

\- Use of pre-trained models

\- Prediction and aggregation of tools



\### CR\_3 - Integration into SmartBugs Workflow

\- Extension of the orchestrator

\- Introduction of an intelligent execution mode



\---



\## 🧩 Architecture Insights



The reverse engineering phase highlighted that:



\- `sb.smartbugs` is the central orchestrator

\- The system is modular and layered

\- Tool execution is isolated via Docker

\- The architecture is suitable for extension at orchestration level



\---



\## ⚠️ Scope of Modifications



The project aims to:



\- Avoid modifications to the core execution pipeline

\- Introduce new components in a modular way

\- Limit impact to a small subset of modules



\---



\## 📁 Repository Structure (Relevant Parts)



\- `sb/` → Core SmartBugs modules

\- `tests/` → Existing test suite

\- `SCsVulLyzer/` → Feature extraction tool

\- `ML\_models/` → Pre-trained models

\- `docs/` → Project documentation (report, diagrams)



\---



\## 🧪 Testing Strategy (Planned)



The testing approach includes:



\- Unit testing for new components

\- Integration testing for the intelligent workflow

\- Regression testing on existing SmartBugs features



\---



\## 📄 Documentation



The full project description, including:



\- Reverse engineering analysis

\- Proposed changes

\- Impact analysis

\- Test plan



is available in the project report.



\---



\## 📌 Notes



This project is developed for academic purposes and is not an official part of the SmartBugs project.

