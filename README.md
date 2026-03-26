# Invoice Me

A full-stack invoice management application for freelancers and small businesses. Create professional invoices, manage clients, generate PDFs, send invoices via email, and schedule recurring billing — all from a single dashboard.

## Features

- **Authentication** — Secure sign-up and login powered by Supabase Auth (ES256 JWT)
- **Client Management** — Add, edit, and organise your client directory
- **Invoice CRUD** — Create, view, update, and delete invoices with line items and tax calculations
- **PDF Generation** — Download publication-ready invoice PDFs
- **Email Delivery** — Send invoices directly to clients with the PDF attached
- **Recurring Schedules** — Automate invoice creation on daily, weekly, or monthly intervals
- **Dashboard** — At-a-glance stats: total clients, invoices, revenue, and recent activity
- **Company Settings** — Configure your business details, logo, and bank/payment information

## Tech Stack

| Layer      | Technology                                            |
|-----------|-------------------------------------------------------|
| Frontend   | Angular 17.3, TypeScript 5.4, SCSS                   |
| Backend    | Python 3.11, FastAPI 0.109, Pydantic 2.5              |
| Database   | PostgreSQL via Supabase (Row Level Security enabled)  |
| Auth       | Supabase Auth (ES256 JWT, JWKS verification)          |
| PDF        | ReportLab                                             |
| Email      | Resend                                                |
| Scheduling | APScheduler                                           |
| Infra      | Docker Compose, Nginx                                 |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- A [Supabase](https://supabase.com) project (free tier works)
- A [Resend](https://resend.com) API key with a verified domain
- (Optional) Node.js 20+ and Python 3.11+ for local development without Docker

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mugonation31/invoice_me.git
cd invoice_me
```

### 2. Set up Supabase

1. Create a new project at [supabase.com](https://supabase.com).
2. Run the migration in `supabase/migrations/001_create_base_tables.sql` via the Supabase SQL Editor. This creates all tables, indexes, RLS policies, and triggers.
3. Note your **Project URL**, **JWT Secret** (Settings > API), and **Database Connection String** (Settings > Database).

### 3. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Fill in `backend/.env`:

| Variable              | Description                                  |
|----------------------|----------------------------------------------|
| `SUPABASE_URL`        | Your Supabase project URL                    |
| `SUPABASE_JWT_SECRET` | JWT secret from Supabase API settings        |
| `DATABASE_URL`        | PostgreSQL connection string from Supabase   |
| `CORS_ORIGINS`        | Comma-separated allowed origins              |
| `RESEND_API_KEY`      | Resend API key                               |
| `RESEND_FROM_EMAIL`   | Verified sender email (on your domain)       |
| `ENVIRONMENT`         | `development` or `production`                |

### 4. Start the application

```bash
docker compose up --build
```

| Service  | URL                          |
|---------|------------------------------|
| Frontend | http://localhost:4201         |
| Backend  | http://localhost:8001         |
| API Docs | http://localhost:8001/docs    |

## Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in values
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
ng serve
```

The frontend runs at http://localhost:4200 and proxies API calls to the backend.

## Running Tests

**Backend unit tests (pytest):**

```bash
cd backend
source venv/bin/activate
pytest -v
```

**Frontend unit tests (Karma/Jasmine):**

```bash
cd frontend
npm test
```

**E2E integration tests (Playwright):**

Requires Docker containers to be running.

```bash
npm install
npx playwright install chromium

# Run without authenticated tests
npx playwright test

# Run the full suite with a Supabase test user
SUPABASE_TEST_EMAIL="user@example.com" SUPABASE_TEST_PASSWORD="pass" npx playwright test
```

The E2E suite covers health checks, CORS configuration, JWT authentication, database connectivity (SSL), and Docker infrastructure.

## Project Structure

```
invoice_me/
├── backend/
│   ├── main.py              # FastAPI application and route definitions
│   ├── auth.py              # JWT verification (ES256/HS256)
│   ├── config.py            # Environment configuration (Pydantic Settings)
│   ├── database.py          # Async PostgreSQL operations (asyncpg)
│   ├── models.py            # Request/response schemas (Pydantic)
│   ├── email_service.py     # Resend email with PDF attachment
│   ├── pdf_generator.py     # Invoice PDF creation (ReportLab)
│   ├── scheduler.py         # APScheduler recurring invoice jobs
│   └── tests/               # 14 unit test modules
├── frontend/
│   └── src/app/
│       ├── auth/             # Login and signup pages
│       ├── clients/          # Client list and form
│       ├── invoices/         # Invoice list, form, and detail
│       ├── schedules/        # Recurring schedule management
│       ├── settings/         # Company and payment settings
│       ├── dashboard/        # Stats and recent invoices
│       ├── core/             # Singleton services (auth, API, Supabase)
│       └── shared/           # Navigation, footer, reusable components
├── supabase/
│   └── migrations/           # SQL schema with RLS policies
├── e2e/                      # Playwright E2E test suite
├── docker-compose.yml
└── playwright.config.ts
```

## API Reference

All endpoints are prefixed with `/api/` and require a valid Bearer token (except `/health`).

| Method           | Endpoint                  | Description                    |
|-----------------|---------------------------|--------------------------------|
| `GET`            | `/health`                 | Health check                   |
| `GET` `POST`     | `/api/clients`            | List or create clients         |
| `GET` `PATCH` `DELETE` | `/api/clients/{id}`  | Get, update, or delete client  |
| `GET` `POST`     | `/api/invoices`           | List or create invoices        |
| `GET` `PATCH` `DELETE` | `/api/invoices/{id}` | Get, update, or delete invoice |
| `GET`            | `/api/invoices/{id}/pdf`  | Download invoice as PDF        |
| `POST`           | `/api/invoices/{id}/send` | Email invoice to client        |
| `GET` `PUT`      | `/api/settings`           | Get or update company settings |
| `GET`            | `/api/dashboard`          | Dashboard statistics           |
| `GET` `POST`     | `/api/schedules`          | List or create schedules       |
| `GET` `PATCH` `DELETE` | `/api/schedules/{id}` | Get, update, or delete schedule |

Interactive API documentation is available at `/docs` (Swagger UI) when the backend is running.

## Database Schema

Five tables with Row Level Security ensuring users can only access their own data:

| Table              | Purpose                                    |
|-------------------|--------------------------------------------|
| `clients`          | Client contact details                     |
| `company_settings` | Business info and bank details (one per user) |
| `invoices`         | Invoice headers (status, dates, totals)    |
| `invoice_line_items` | Line items linked to invoices            |
| `invoice_schedules`  | Recurring invoice schedule definitions   |

All tables include `created_at` and `updated_at` timestamps with automatic update triggers.

## Security

- Row Level Security on all database tables — users can only access their own data
- ES256 JWT verification via JWKS public keys
- Non-root Docker container
- HTML-escaped email templates to prevent injection
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy) on the frontend
- Secrets excluded from Docker images via `.dockerignore`
- SSL-encrypted database connections

## Licence

This project is for personal and educational use.
