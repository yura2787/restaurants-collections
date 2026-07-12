# 🍽️ TasteMap — Restaurant Discovery Platform

A full-stack web application for discovering, browsing, and saving restaurants. Built with a microservice architecture, async Python backend, and a premium responsive frontend.

**Live demo:** [http://localhost](http://localhost) *(self-hosted via Docker)*

---

## 📸 Preview

> Browse restaurants with filters, save favourites, explore an interactive map, and manage your profile — all in one place.

---

## 📸 Screenshots

<img width="3402" height="1924" alt="2026-07-12_19-14" src="https://github.com/user-attachments/assets/3332bcf9-252b-46c5-ad19-6562661bd0f2" />

<img width="3412" height="1904" alt="2026-07-12_19-14_1" src="https://github.com/user-attachments/assets/03caa86b-c898-4704-a8ab-4ddcdce98401" />

<img width="2620" height="1644" alt="2026-07-12_19-22" src="https://github.com/user-attachments/assets/04201828-a38f-4a2c-9dc1-1b0aa750daea" />

<img width="2974" height="1202" alt="2026-07-12_19-22_1" src="https://github.com/user-attachments/assets/a5853cd1-b404-42c2-9dbb-5636efb19cbe" />

<img width="3332" height="1890" alt="2026-07-12_19-23_3" src="https://github.com/user-attachments/assets/fa2d8fc1-62c0-4348-b388-6b6729089423" />

<img width="2894" height="1774" alt="2026-07-12_19-23" src="https://github.com/user-attachments/assets/edafeb41-d8b6-47fe-809d-0f0beeb867f7" />

<img width="3390" height="1820" alt="2026-07-12_19-23_2" src="https://github.com/user-attachments/assets/93f1e837-3755-4e58-b020-21c14676ec32" />

<img width="2844" height="1050" alt="2026-07-12_19-23_1" src="https://github.com/user-attachments/assets/ba5be506-a37e-4137-b75f-9022ca49d7ce" />

<img width="3392" height="1772" alt="2026-07-12_19-24" src="https://github.com/user-attachments/assets/e7e8e390-bbb6-4391-8b85-2ea4b7a5fab9" />

<img width="3388" height="1654" alt="2026-07-12_19-24_1" src="https://github.com/user-attachments/assets/6234ec9a-ed8e-4267-8f63-91743e7282e0" />

---

## ✨ Features

- 🔐 **JWT Authentication** — secure sign-up / sign-in with access & refresh tokens, email verification
- 🏪 **Restaurant Catalog** — cards with images, cuisine tags, price range badges, and menu previews
- 🔍 **Filters & Sorting** — filter by cuisine category, sort by name or date
- ♥ **Favourites** — AJAX toggle with instant feedback toasts, no page reload
- 🗺️ **Interactive Map** — Leaflet.js map with restaurant markers and popups
- 🖼️ **Image Lightbox** — click any restaurant photo to open a fullscreen viewer
- 👤 **Profile Page** — user stats (favourites count, reviews count)
- 🌙 **Dark / Light Theme** — toggle persisted in localStorage, no flash on load
- 📧 **Email Notifications** — transactional emails via RabbitMQ message queue
- 📱 **Fully Responsive** — mobile-first layout with Bootstrap grid

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (port 80)                  │
│         Rate limiting · Security headers            │
└──────────────┬──────────────────┬───────────────────┘
               │                  │
       /api/*  │                  │  /*
               ▼                  ▼
     ┌──────────────┐    ┌──────────────────┐
     │  Backend API │    │    Frontend      │
     │  FastAPI     │    │  FastAPI + Jinja2│
     │  port 9999   │    │  port 12345      │
     └──────┬───────┘    └──────────────────┘
            │
     ┌──────┴───────────────────┐
     │                          │
     ▼                          ▼
┌─────────────┐       ┌──────────────────────┐
│  PostgreSQL │       │  Notification Service │
│  (Neon)     │       │  RabbitMQ consumer    │
└─────────────┘       │  Sends emails via SMTP│
                      └──────────────────────┘
```

**Services:**
| Service | Technology | Role |
|---|---|---|
| `backend_api` | FastAPI + SQLAlchemy (async) | REST API, business logic |
| `frontend` | FastAPI + Jinja2 + Bootstrap | Server-rendered UI |
| `notification` | Python + Pika (RabbitMQ) | Async email delivery |
| `nginx` | Nginx Alpine | Reverse proxy, rate limiting |
| `database` | PostgreSQL 16 | Primary data store |

---

## 🛠️ Tech Stack

**Backend**
- Python 3.12, FastAPI, SQLAlchemy 2.0 (async), asyncpg
- JWT (PyJWT) — access + refresh tokens
- Passlib + bcrypt — password hashing
- Pika — RabbitMQ producer/consumer
- aioboto3 — Cloudflare R2 (S3-compatible) image storage
- Pydantic v2 — schema validation

**Frontend**
- FastAPI + Jinja2 templates
- Bootstrap 5, custom CSS with CSS variables
- Vanilla JS — AJAX favourites, theme toggle, lightbox, toast notifications
- Leaflet.js — interactive restaurant map
- Playfair Display + Inter — premium typography

**Infrastructure**
- Docker + Docker Compose (5 services)
- Nginx — reverse proxy, rate limiting (`10r/s` API, `5r/m` login), security headers
- PostgreSQL 16 with health checks
- Neon (serverless Postgres), Cloudflare R2, CloudAMQP

**Testing**
- pytest + pytest-asyncio
- SQLite in-memory test database
- 11 tests covering auth and restaurant endpoints

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose installed

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yura2787/restaurants-collections.git
   cd restaurants-collections
   ```

2. Create a `.env` file in the root with the following variables:
   ```env
   # PostgreSQL
   POSTGRES_USER=...
   POSTGRES_PASSWORD=...
   POSTGRES_HOST=...
   POSTGRES_DB=...
   POSTGRES_PORT=5432

   # JWT
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256

   # Cloudflare R2 (image storage)
   R2_ACCESS_KEY=...
   R2_SECRET_KEY=...
   R2_BUCKET_NAME=...
   R2_ENDPOINT_URL=...
   R2_PUBLIC_URL=...

   # RabbitMQ
   RMQ_HOST=...
   RMQ_PORT=5671
   RMQ_USER=...
   RMQ_PASS=...

   # SMTP (email)
   SMTP_HOST=...
   SMTP_PORT=...
   SMTP_USER=...
   SMTP_PASSWORD=...
   ```

3. Start all services:
   ```bash
   docker compose up --build
   ```

4. Open [http://localhost](http://localhost) in your browser.

---

## 📁 Project Structure

```
restaurants-collections/
├── backend_api/          # REST API (FastAPI)
│   └── app/
│       ├── applications/
│       │   ├── Restaurants/  # CRUD, schemas, router
│       │   ├── auth/         # Login, refresh token
│       │   ├── users/        # Profile, favourites
│       │   └── feedback/     # Reviews
│       └── tests/            # pytest test suite
├── frontend/             # Server-rendered UI (FastAPI + Jinja2)
│   └── app/
│       ├── templates/    # HTML templates
│       ├── static/
│       │   ├── css/      # base.css — full design system
│       │   └── js/       # app.js — theme, favourites, lightbox
│       └── routers/
├── notification_service/ # Email worker (RabbitMQ consumer)
├── nginx/                # nginx.conf — reverse proxy config
└── docker-compose.yaml
```

---

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens with expiry (access short-lived, refresh long-lived)
- Nginx rate limiting on login endpoint (`5r/m`) to prevent brute-force
- Security headers: `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`
- Non-root Docker users (`appuser`) in all service containers
- Environment variables — no secrets in source code

---

## 👥 Team

This is a **group university graduation project** developed collaboratively by a team of students.

