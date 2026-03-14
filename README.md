
# End-to-End Data Engineering Pipeline for Olist E-commerce Data

## Project Overview
This project builds an end-to-end data engineering pipeline for processing and analyzing the Olist e-commerce dataset.
The system automatically ingests raw data, transforms it using dbt, and prepares structured datasets for analytics using the Data Vault architecture.
The pipeline demonstrates key Data Engineering concepts, including:
- Data ingestion
- Data transformation
- Data warehouse modeling (Data Vault)
- Workflow orchestration
- Containerized deployment

## System Architecture
![KienTruc](images/kientruc.png)
## Dataset
- Dataset used in this project:
- Olist Brazilian E-commerce Dataset
- Source: Kaggle

## Technology Stack
| Layer               | Tool           |
| ------------------- | -------------- |
| Programming         | Python         |
| Database            | PostgreSQL     |
| Data Transformation | dbt            |
| Orchestration       | Apache Airflow |
| Containerization    | Docker         |
| Data Modeling       | Data Vault 2.0 |
## Running the Project
docker compose up -d
