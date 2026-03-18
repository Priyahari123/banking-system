# Mini Banking System

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Python](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.x-green.svg)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/celery-5.x-orange.svg)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/redis-7.x-red.svg)](https://redis.io/)

---



## Objective
This project is designed to test and demonstrate skills in:

- Role-based permissions
- API design
- Business logic
- Exception handling
- Asynchronous tasks
- Clean and maintainable Django code

---

## Overview
This Mini Banking System implements three user roles:

| Role           | Access Rights |
|----------------|---------------|
| Customer       | Can view only their own account and loans. Can pay loans. Cannot view other customers. |
| Bank Employee  | Can view all customer accounts but cannot view other employees. |
| Bank Manager   | Can view and manage all accounts, employees, and loans. Can create users but cannot delete or update them. |

---

## Core Concepts
- **Users:** Role-based permissions; Managers can create users.  
- **Bank Accounts:** Track balances; access controlled by role.  
- **Loans:** Track total amount, amount paid, and status. Only valid payments allowed.  

---

## API Endpoints & Business Rules
1. **View Account Details**:  
   - Customer sees own account.  
   - Employee sees all customer accounts.  
   - Manager sees all accounts.  

2. **Pay Loan**:  
   - Reduces loan balance.  
   - Updates loan status (`pending` → `completed`).  
   - Prevents invalid or overpayments.  

3. **Apply Interest**:  
   - Manager-only operation.  
   - Applies interest to all customer accounts asynchronously using Celery.  

4. **Create Users**:  
   - Manager-only operation.  
   - Employees cannot create users.  
   - Managers cannot delete or update existing users.  

---

## Validation & Exception Handling
- Role-based access enforced.  
- Invalid operations return clear, descriptive messages.  
- Loan payments are validated for overpayment and access.  

---

## Asynchronous Tasks
- Heavy operations like **interest application** are handled by Celery workers.  
- Celery tasks update account balances asynchronously.  
- All updates are logged in `bank_app.log`.  

---

## Project Setup (Windows / GitHub)

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd bank_system

Create & Activate Virtual Environment
python -m venv venv
venv\Scripts\activate


Install Dependencies
pip install -r requirements.txt


Configure Django Settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

Run Migrations
python manage.py makemigrations
python manage.py migrate

Create Superuser (Manager)
python manage.py createsuperuser


Start Django Server
python manage.py runserver

Run Redis Server
redis-server

Start Celery Worker
python -m celery -A bank_system worker --loglevel=info -P solo


This is the input format 
bank_input_format.txt
---------------------------------------

LOGIN  - /api/login/
{
  "email": "manager123@gmail.com",
  "password": "test123"
}
----------------------------------------------

CREATE USER BY MANAGER -/api/user/create/
{
  "email": "customer1@bank.com",
  "mobile_number": "9876543210",
  "role": "customer",
  "password": "test123",
  "customer_id": "CUST1001"
}
------------------------------------------------

LOAN CREATED BY MANAGER -/api/loan/create/
{
  "customer_id": "CUST001",
  "total_amount": 100000
}
-------------------------------------------------------

PAY LOAN FOR CUSTOMER -/api/loan/pay/
{
  "customer_id": "CUST1001",
  "loan_id": 5,
  "amount": 30000
}
----------------------------------------------------------
APPLY INTEREST BY MANAGER -/api/account/apply_interest/
{
  "interest_percent": 10
}
----------------------------------------------------------


Perfect! You can turn this into a **well-formatted README.md file** so it’s easy to read and use as a reference for your APIs. Here’s a professional and clean version using Markdown:

---

````markdown id="bank_readme"
# Bank Project API Reference

This document provides the API endpoints and sample inputs for the banking system.

---

## 1️⃣ LOGIN

**Endpoint:** `/api/login/`  
**Method:** POST  

**Request Body:**
```json
{
  "email": "manager123@gmail.com",
  "password": "test123"
}
````

---

## 2️⃣ CREATE USER BY MANAGER

**Endpoint:** `/api/user/create/`
**Method:** POST

**Request Body:**

```json
{
  "email": "customer1@bank.com",
  "mobile_number": "98765******",
  "role": "customer",
  "password": "test123",
  "customer_id": "CUST1001"
}
```

---

## 3️⃣ LOAN CREATED BY MANAGER

**Endpoint:** `/api/loan/create/`
**Method:** POST

**Request Body:**

```json
{
  "customer_id": "CUST001",
  "total_amount": 100000
}
```

---

## 4️⃣ PAY LOAN FOR CUSTOMER

**Endpoint:** `/api/loan/pay/`
**Method:** POST

**Request Body:**

```json
{
  "customer_id": "CUST1001",
  "loan_id": 5,
  "amount": 30000
}
```

---

## 5️⃣ APPLY INTEREST BY MANAGER

**Endpoint:** `/api/account/apply_interest/`
**Method:** POST

**Request Body:**

```json
{
  "interest_percent": 10
}
```

---


## CHECK THE CUSTOMER LOAN DETAILS
**Endpoint:** `/api/account/CUST1001/`
**Method:** GET

**Response:**
```json
{
  "customer_id": "CUST1001",
  "email": "customer1@bank.com",
  "mobile_number": "987654***",
  "role": "customer",
  "loans": [
    {
      "loan_id": 5,
      "total_amount": 100000,
      "paid_amount": 30000,
      "interest_percent": 10
    }
  ]
}
```
---




