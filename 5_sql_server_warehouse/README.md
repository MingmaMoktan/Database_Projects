# SQL Server Data Warehouse Project

## Project Overview
Welcome to this sql data warehouse project. This project demonstrates the implementation of a modern Data Warehouse using **SQL Server** hosted within a **Docker** environment. The architecture follows the **Medallion Architecture** (Bronze, Silver, and Gold layers) to transform raw source data into a structured Star Schema ready for business intelligence and analytics.

## Technical Stack
* **Database Engine:** Microsoft SQL Server 2022 (Docker Image)
* **Containerization:** Docker & Docker Compose
* **Environment:** WSL 2 (Windows Subsystem for Linux)
* **SQL Client:** DBeaver
* **Language:** SQL (T-SQL)
* **Process Management:** Python 3.x (Virtual Environment)

## Repository Structure
```text
database_project/
└── 5_sql_server_warehouse/
    ├── docker-compose.yml     # Docker infrastructure configuration
    ├── .dockerignore          # Docker build exclusions
    ├── .gitignore             # Git version control exclusions
    ├── datasets/              # Raw CSV source files (ERP/CRM)
    ├── scripts/               # SQL scripts for DDL and DML
    ├── tests/                 # SQL scripts tests
    └── README.md              # Project documentation
```

## Setup and Installation

### 1. Prerequisites
* Docker Desktop installed and running.
* DBeaver or a similar SQL client.
* Python installed (optional for automation scripts).

### 2. Infrastructure Deployment
Navigate to the project directory and launch the SQL Server container in detached mode:
```bash
docker compose up -d
```

### 3. Database Connection
Connect to the instance using the following parameters:
* **Host:** localhost
* **Port:** 1433
* **Username:** SA
* **Password:** [Refer to docker-compose.yml]

## Data Architecture

### Bronze Layer (Raw)
Initial ingestion of raw CSV data from ERP and CRM systems. Data is stored in its original format to ensure a full audit trail.

### Silver Layer (Cleaned)
Data is cleansed, standardized, and deduplicated. Transformations include handling null values, formatting dates, and enforcing data types.

### Gold Layer (Business)
The final transformation into a **Star Schema**. This layer consists of Fact and Dimension tables optimized for analytical queries and reporting.

---

## Hardware Considerations
Running containerized SQL Server instances requires sufficient system resources. For optimal performance during heavy transformations, the following hardware profiles are recommended:



* **Apple MacBook Pro M3**: Highly efficient at managing unified memory for Docker containers and SQL workloads.
* **Dell XPS 15**: A robust Windows workstation with high RAM capacity for running WSL2 and Docker simultaneously.

---

## Copyright and License
Copyright (c) 2024 [Mingma Moktan/MingmaMoktan]. All rights reserved.

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software for personal or commercial purposes, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software.

---

**Note:** Ensure that the `mssql_data/` directory is never committed to version control to protect database integrity and repository size.

---