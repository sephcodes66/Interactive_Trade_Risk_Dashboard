### How the RITA Prototype Demonstrates Key Skills for the IT Business Analyst Role

This document maps the features and development process of the RITA (Real-time Interactive Trading and Analytics) prototype to the core responsibilities and profile requirements for the Risk Tools and Analytics team.

**1. Gathering, Analysing, and Prototyping**

*   **Requirement:** "Gathering, analysing and assessing business and system requirements and designing solutions... prepare forward-looking prototypes."
*   **Showcased by RITA:** The entire project is a high-fidelity, "forward-looking prototype" built from a set of initial requirements (`plan.pdf`). The project's structure, from the `project_plan.md` to the final application, demonstrates the ability to analyze a business need (pre-trade risk assessment), design a complete software solution, and execute it.

**2. Development of Risk Models and Applications**

*   **Requirement:** "Supporting development, testing and maintenance of risk models and RITA application."
*   **Showcased by RITA:**
    *   **Risk Model Development:** The `src/risk_engine.py` file contains a complete, functional implementation of the historical Value at Risk (VaR) model, a standard financial risk model.
    *   **Application Development:** The entire `src` directory represents the development of the RITA application, using modern Python libraries (SQLAlchemy, Pandas, Streamlit) and a structured, maintainable architecture.

**3. Quality Assurance and User Acceptance Testing (UAT)**

*   **Requirement:** "Performing thorough quality assurance... formulating test approach, defining acceptance criteria, preparating test data and test cycle execution."
*   **Showcased by RITA:**
    *   **Test Approach & UAT:** The `TESTING.md` file serves as a formal UAT plan, explicitly defining test scenarios, actions, and acceptance criteria for key application features.
    *   **Unit Testing:** The `tests/` directory contains a suite of unit tests written with `pytest`. These tests isolate and verify the backend logic, demonstrating a commitment to code quality and preventing regressions.
    *   **Test Data Preparation:** The `data/` directory and the `src/ingest_data.py` script show the process of sourcing, selecting, and preparing a consistent dataset for testing and analysis.

**4. Complex Data Analysis and Visualization with Python**

*   **Requirement:** "Performing complex data analysis and data visualisation tasks... strong analytical skills, ability to produce clear graphical representations and data visualisations, preferably experienced with Python."
*   **Showcased by RITA:**
    *   **Data Analysis:** The backend (`src/risk_engine.py`) performs complex analysis by fetching historical data, calculating daily percentage returns for a multi-asset portfolio, and simulating thousands of potential profit/loss scenarios.
    *   **Data Visualization:** The frontend (`src/app.py`) uses Python's `plotly` library to generate clear, interactive histograms of the simulated P/L distributions. This directly addresses the need to create "clear graphical representations" to make complex data understandable.

**5. Hands-on SQL and PostgreSQL Experience**

*   **Requirement:** "Knowledge of data analysis tools and hands on experience with writing SQL queries, preferably in PostgreSQL."
*   **Showcased by RITA:** SQL is used extensively and efficiently throughout the project's backend:
    *   **Schema Definition:** `CREATE TABLE` statements in `src/ingest_data.py` define the database structure.
    *   **Data Ingestion:** `INSERT ... ON CONFLICT` queries ensure robust and non-duplicative data loading.
    *   **Targeted Data Retrieval:** The `src/portfolio.py` module uses a `JOIN` with a subquery to efficiently fetch only the most recent price for each stock.
    *   **Advanced Analytics:** The `src/risk_engine.py` module uses a Common Table Expression (CTE) with a `ROW_NUMBER()` window function to perform complex filtering of historical time-series data directly within the PostgreSQL database for maximum efficiency.

**6. Software Project Management and Methodology**

*   **Requirement:** "Previous experience in software project management and knowledge of the related methodology and tools."
*   **Showcased by RITA:** The project is managed using standard software development practices:
    *   **Phased Development:** The project followed the clear, phased plan outlined in `project_plan.md`.
    *   **Dependency Management:** A `requirements.txt` file tracks all project dependencies.
    *   **Version Control Readiness:** A comprehensive `.gitignore` file ensures that only essential source code is committed.
    *   **Professional Structure:** The use of a `src` directory layout, a `setup.py` file, and separate `tests` and `data` directories demonstrates knowledge of professional project structure.

**7. Critical Thinking and Problem-Solving**

*   **Requirement:** "Excellent communication skills, attention to detail, critical thinking, problem solving attitude."
*   **Showcased by RITA:** The development process involved iteratively identifying and solving numerous real-world software engineering challenges, including:
    *   Diagnosing and fixing database connection and authentication errors.
    *   Resolving Python module import conflicts by restructuring the project.
    *   Debugging data type mismatches between the application and the database (`bigint` overflow).
    *   Refining the data ingestion strategy to be both efficient and correct, ensuring all required data is present.