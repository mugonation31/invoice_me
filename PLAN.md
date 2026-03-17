# invoice_me Development Plan

## Overview
Full-stack invoice generation app. Angular 17 + FastAPI + Supabase + SendGrid + Docker.
Replicates TODO app architecture from ~/workspace/projects/TODO.

## Phase 1: Project Scaffolding

- [x] **Task 1.1** - Backend scaffolding (S): backend/ with main.py, config.py, auth.py, models.py, database.py, requirements.txt, .env.example, Dockerfile, .dockerignore
- [x] **Task 1.2** - Frontend scaffolding (M): Angular 17 CLI app with standalone components, SCSS, environment.ts, nginx.conf, Dockerfile, .dockerignore
- [x] **Task 1.3** - Docker and env setup (S): docker-compose.yml, .gitignore, .env.example
- [x] **Task 1.4** - Supabase migrations (M): supabase/migrations/001_create_base_tables.sql with all tables, RLS policies, indexes, triggers

## Phase 2: Auth System

- [x] **Task 2.1** - Frontend SupabaseService + auth guard (S)
- [x] **Task 2.2** - Login page (S)
- [x] **Task 2.3** - Signup page (S)
- [x] **Task 2.4** - Backend auth module (S)
- [x] **Task 2.5** - Navigation component (S)

## Phase 3: Client Management

- [x] **Task 3.1** - Client backend CRUD (M)
- [x] **Task 3.2** - Client frontend model + service (S)
- [x] **Task 3.3** - Client list page (M)
- [x] **Task 3.4** - Client form component (S)

## Phase 4: Company/Payment Settings

- [x] **Task 4.1** - Settings backend (S)
- [x] **Task 4.2** - Settings frontend page (M)

## Phase 5: Invoice CRUD — Backend

- [x] **Task 5.1** - Invoice backend models (S)
- [x] **Task 5.2** - Invoice database operations (M)
- [x] **Task 5.3** - Invoice API endpoints (M)

## Phase 6: Invoice CRUD — Frontend

- [x] **Task 6.1** - Invoice frontend models + service (S)
- [x] **Task 6.2** - Invoice list page (M)
- [x] **Task 6.3** - Invoice form page (L)
- [x] **Task 6.4** - Invoice detail/view page (S)

## Phase 7: Invoice PDF Generation

- [x] **Task 7.1** - PDF generation backend (M)
- [x] **Task 7.2** - PDF download endpoint + frontend button (S)

## Phase 8: Email Sending

- [x] **Task 8.1** - SendGrid email backend (M)
- [x] **Task 8.2** - Send invoice endpoint + UI (S)

## Phase 9: Scheduling

- [x] **Task 9.1** - Schedule database + models (S)
- [x] **Task 9.2** - Scheduler backend with APScheduler (M)
- [x] **Task 9.3** - Schedule API + frontend UI (M)

## Phase 10: Dashboard + Polish

- [ ] **Task 10.1** - Dashboard backend stats endpoint (S)
- [ ] **Task 10.2** - Dashboard frontend page (M)
- [ ] **Task 10.3** - App routing + final integration (S)

## Risks
- ReportLab chosen over WeasyPrint (simpler Docker builds)
- SendGrid requires API key + verified sender
- APScheduler needs DB persistence to survive restarts
- Invoice number uniqueness needs DB-level locking

## Decisions
- Invoice numbers: per-user sequential (INV-0001...)
- Currency: GBP only
- Overdue status: auto-set by background job
- PDF preview before sending: yes
