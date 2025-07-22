# 🏦 Loan Approval System (Dockerized Django + PostgreSQL)

This is a Django-based Loan Approval System that helps register customers, check loan eligibility based on historical data, create and view loans. It is fully containerized using Docker and uses PostgreSQL as the database.
[video demo](https://drive.google.com/file/d/1ZgqTTLtB80qZcNcdBj-4NIvbakctFXTd/view?usp=sharing)

---

## ✅ Features

- Customer Registration
- Loan Eligibility Check (with Credit Scoring)
- Create Loan
- View Single or All Loans for a Customer
- Data ingestion from Excel files (`loan_data.xlsx`, `customer_data.xlsx`)
- Dockerized setup with PostgreSQL

---

## 🧱 Tech Stack

- Python 3.10
- Django 5.2.4
- Django REST Framework
- PostgreSQL 16.9
- Docker & Docker Compose
- Celery (Optional for async ingestion)

---

### 🔧 Folder structure

```bash
loan_project/
├── api/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── management/commands/ingest_data.py
│   └── ...
├── loan_project/
│   └── settings.py
|   └──.env
├── customer_data.xlsx
├── loan_data.xlsx
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
### Modify .env 
```bash
DEBUG=True
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```
### Modify DockerFile
```bash
environment:
POSTGRES_DB: postgres
POSTGRES_USER: postgres
POSTGRES_PASSWORD: password
```
### Build and Start Containers

```bash
docker-compose up --build
```

# Final
This will:

Start PostgreSQL on port 5432

Build your Django app

Run migrations

Ingest data from Excel files

Start the Django server on http://localhost:8000
