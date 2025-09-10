# 💳 Credit Loan Management API  

A Django REST Framework application (containerized with Docker) for managing customers and loans with automated credit eligibility checks, compound-interest EMI calculations, and Celery-powered background tasks.  

---

## 📌 Features  

- **Customer Management**  
  - Register new customers with auto-approved credit limit (`36 × monthly_salary`, rounded to nearest lakh).  

- **Loan Management**  
  - Check loan eligibility using a credit score derived from historical loans.  
  - Create new loans with corrected interest rates if required.  
  - View details of a single loan or all loans for a customer.  

- **Financial Calculations**  
  - Compound-interest–based EMI calculation.  
  - Credit score influenced by:  
    - Past loans paid on time  
    - Number of past loans  
    - Loan activity in current year  
    - Loan volume vs. approved limit  
    - Current EMIs vs. salary (≥50% → rejection)  

- **Infrastructure**  
  - Django REST API served with **Gunicorn**  
  - **Postgres** for persistence  
  - **Redis + Celery** for async tasks (loading historical data from Excel)  
  - Fully **Dockerized** (`docker-compose` ready)  

---

## 🛠️ Tech Stack  

- **Backend:** Django, Django REST Framework  
- **Database:** PostgreSQL  
- **Task Queue:** Celery + Redis  
- **Containerization:** Docker & Docker Compose  

---

## 📂 Project Structure  

```plaintext
myproject/
│── creditcardapp/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── urls.py
│   ├── views.py
│── data/                # Excel data (loan_data.xlsx etc.)
│── myproject/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│── staticfiles/
│── Dockerfile
│── docker-compose.yml
│── entrypoint.sh
│── requirements.txt
│── manage.py
│── README.md
```

##🚀 Getting Started

**1. Clone the repository**

git clone https://github.com/HarshGosula/credit-loan-manager.git

cd myproject

**2. Create .env file**

POSTGRES_DB=mydb  
POSTGRES_USER=myuser  
POSTGRES_PASSWORD=mypassword  
DJANGO_SECRET_KEY=supersecretkey  
DJANGO_DEBUG=1  

**3. Build and start services**

docker-compose up --build -d


This starts:

Django app → http://localhost:8000

PostgreSQL → port 5432

Redis → port 6379
