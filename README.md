
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

## Business Context
The project is built around the Olist Brazilian E-commerce public dataset, a public dataset centered on real e-commerce activity in Brazil and collected by Olist from its marketplace ecosystem.
It records around 100,000 orders between 2016 and 2018 and provides a full business view across order status, product attributes, prices, payment methods, freight, customer location, customer reviews, and geolocation references mapped from Brazilian zip codes to latitude/longitude.

Because the dataset reflects how online commerce operates in Brazil, the project is framed not just as a technical data pipeline, but as a business analytics and decision-support system.
The goal is to turn Olist's collected operational data into structured marts, BI dashboards, and ML workflows that support analysis of sales performance, fulfillment quality, customer demand, and near-term business signals.

This business context makes the project suitable for three practical decision-making scenarios:
- demand planning: identify products that are likely to become bestsellers in the next 7 days so inventory and marketing can be prioritized early
- order operations: identify orders that are at risk of not completing successfully so operations can intervene sooner
- regional planning: identify cities or regions that are likely to show high demand so campaign budget and logistics readiness can be allocated better

Instead of stopping at raw reporting, the project turns these business questions into analytics-ready marts, BI views, and ML workflows that help answer not just what happened, but what is likely to happen next.

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
| BI Dashboard        | Apache Superset |
| Containerization    | Docker         |
| Data Modeling       | Data Vault 2.0 |
## Running the Project
docker compose up -d

Superset runs at:

```text
http://localhost:8088
```

Default account:

```text
admin / admin
```

Airflow runs at:

```text
http://localhost:8080
```

Default account:

```text
airflow / airflow
```

Connect Superset to the mart warehouse with:

```text
postgresql+psycopg2://airflow:airflow@postgres:5432/ecommerce
```

See `docs/superset_bi_setup.md` for the recommended BI dashboard around the 3 predictive mart use cases.
