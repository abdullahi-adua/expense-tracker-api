# Expense Tracker API

A Django REST Framework API for tracking personal income and expenses, with categories, filtering, monthly summaries, and JWT-based authentication.

## Features

- JWT authentication for registration, login, and token refresh
- User-owned category management for income and expense types
- Full CRUD support for transactions
- Filtering and search by date range, category, type, and description
- Pagination across list endpoints
- Summary and monthly aggregation APIs
- Ownership enforcement so users only access their own data
- Rate limiting for auth endpoints
- Swagger/OpenAPI docs
- Automated tests covering auth, CRUD, filtering, aggregation, and throttling

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6.1.1, Django REST Framework 3.18.1 |
| Database | PostgreSQL 16 |
| Authentication | djangorestframework-simplejwt |
| Filtering | django-filter |
| API Docs | drf-spectacular |
| Env config | django-environ |
| Containerization | Docker + Docker Compose |
| Testing | Django TestCase + DRF APITestCase |

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- [Git](https://git-scm.com/)

## Quick Start

### 1. Clone the repository

```bash
git clone <https://github.com/abdullahi-adua/expense-tracker-api>
cd Expense_Tracker_API
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Update the values in `.env` as needed:

- `SECRET_KEY` — set a secure Django secret key
- `DEBUG` — usually `True` for local development
- `ALLOWED_HOSTS` — comma-separated hostnames, for example `localhost,127.0.0.1,web`
- `POSTGRES_PASSWORD` — strong database password

You can generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Start the app

```bash
docker compose up --build -d
```

Wait a few moments for PostgreSQL to become ready, then run database migrations:

```bash
docker compose exec web python manage.py migrate
```

Create an admin account if needed:

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Access the API

| Service | URL |
|---|---|
| API root | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| OpenAPI schema | http://localhost:8000/api/schema/ |
| Django admin | http://localhost:8000/admin/ |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/login/` | Obtain JWT access and refresh tokens |
| `POST` | `/api/auth/refresh/` | Refresh an access token |
| `GET` / `POST` | `/api/categories/` | List or create categories |
| `GET` / `PUT` / `PATCH` / `DELETE` | `/api/categories/{id}/` | Retrieve, update, or delete a category |
| `GET` / `POST` | `/api/transactions/` | List or create transactions |
| `GET` / `PUT` / `PATCH` / `DELETE` | `/api/transactions/{id}/` | Retrieve, update, or delete a transaction |
| `GET` | `/api/transactions/summary/` | Totals for income, expenses, and net values over a date range |
| `GET` | `/api/transactions/monthly/` | Monthly per-category totals for a given year and month |

All authenticated endpoints require the `Authorization` header in this format:

```http
Authorization: Bearer your_access_token
```

## Example Usage

### Register a user

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "Str0ng-Pass-2026",
    "password_confirm": "Str0ng-Pass-2026"
  }'
```

### Log in

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "Str0ng-Pass-2026"
  }'
```

Example response:

```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

### Get a summary for a date range

```bash
curl -H "Authorization: Bearer your_access_token" \
  "http://localhost:8000/api/transactions/summary/?date_from=2026-10-01&date_to=2026-10-31"
```

Example response:

```json
{
  "date_from": "2026-10-01",
  "date_to": "2026-10-31",
  "total_income": "5000.00",
  "total_expense": "1500.00",
  "net": "3500.00",
  "transaction_count": 15
}
```

### Get a monthly breakdown by category

```bash
curl -H "Authorization: Bearer your_access_token" \
  "http://localhost:8000/api/transactions/monthly/?year=2026&month=10"
```

Example response:

```json
{
  "year": 2026,
  "month": 10,
  "by_category": [
    {"category": "Food", "type": "expense", "total": "1500.00", "count": 3},
    {"category": "Salary", "type": "income", "total": "5000.00", "count": 1}
  ]
}
```

## Running Tests

```bash
docker compose exec web python manage.py test expenses -v 2
```

This project includes coverage for CRUD operations, authentication, filtering, aggregation, pagination, throttling, and ownership rules.

## Author

Adua Abdullahi

- GitHub: @abdullahi-adua
- Email: abdullahiadua6@gmail.com
