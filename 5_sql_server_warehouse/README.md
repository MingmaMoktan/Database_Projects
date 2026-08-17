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
    ├── docs/                  # Documentation, diagrams, and data catalogs
    │   ├── Data_Architecture.png
    │   ├── data_catalogue.md
    │   ├── Data_model.png
    │   └── Integration_model.png
    ├── datasets/              # Raw CSV source files (ERP/CRM)
    ├── scripts/               # SQL scripts for DDL and DML
    ├── tests/                 # SQL scripts tests
    ├── .dockerignore          # Docker build exclusions
    ├── docker-compose.yml     # Docker infrastructure configuration
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

---

## Data Architecture & Models

### 1. Data Architecture

* **Bronze Layer (Raw):** Initial ingestion of raw CSV data from ERP and CRM systems. Data is stored in its original format to ensure a full audit trail.
* **Silver Layer (Cleaned):** Data is cleansed, standardized, and deduplicated. Transformations include handling null values, formatting dates, and enforcing data types.
* **Gold Layer (Business):** The final transformation into a **Star Schema**. This layer consists of Fact and Dimension tables optimized for analytical queries and reporting.

### 2. Data Model & Schema Design

The Gold layer uses a dimensional modeling approach separating descriptive attributes (`dim_customers`, `dim_product`) from transactional event metrics (`fact_sales`). For detailed field definitions, consult the [Data Catalog](https://www.google.com/search?q=docs/data_catalogue.md).

### 3. Integration Workflow

Data flows systematically from source files through the Bronze ingestion tables, undergoes quality and standardization rules in the Silver stage, and finally populates the dimensional Star Schema in the Gold layer.

---

## Hardware Considerations

Running containerized SQL Server instances requires sufficient system resources. For optimal performance during heavy transformations, the following hardware profiles are recommended:

* **Apple MacBook Pro M3**: Highly efficient at managing unified memory for Docker containers and SQL workloads.
* **Dell XPS 15**: A robust Windows workstation with high RAM capacity for running WSL2 and Docker simultaneously.

---

## Copyright and License

Copyright (c) 2024 [Mingma Moktan/MingmaMoktan]. All rights reserved.

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software for personal or commercial purposes, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software.

```