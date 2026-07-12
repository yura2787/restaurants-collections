# 🍽️ TasteMap — Restaurant Discovery Platform

A full-stack web application for discovering, browsing, and saving restaurants. Built with a microservice architecture, async Python backend, and a premium responsive frontend.

**Live demo:** [http://localhost](http://localhost) *(self-hosted via Docker)*

---

## 📸 Preview

> Browse restaurants with filters, save favourites, explore an interactive map, and manage your profile — all in one place.

---

## 📸 Screenshots

<img width="3402" height="1924" alt="2026-07-12_19-14" src="https://github.com/user-attachments/assets/f4678323-cd7d-41af-b13d-45ae1371aae4" />

<img width="3412" height="1904" alt="2026-07-12_19-14_1" src="https://github.com/user-attachments/assets/231d7737-106e-4a73-8864-f9ba95aa3910" />


<img width="2620" height="1644" alt="2026-07-12_19-22" src="https://github.com/user-attachments/assets/b63fb8c5-7598-4124-8bc6-af956e0e96cb" />


<img width="2894" height="1774" alt="2026-07-12_19-23" src="https://github.com/user-attachments/assets/48e76568-2b1d-41bd-b37b-83e6f38a31da" />

<img width="2974" height="1202" alt="2026-07-12_19-22_1" src="https://github.com/user-attachments/assets/733e008c-d8ba-498a-befa-4e211d4c3d3a" />

<img width="2844" height="1050" alt="2026-07-12_19-23_1" src="https://github.com/user-attachments/assets/d97d8b45-9613-4380-95ab-ecdd657a88c4" />






<img width="3390" height="1820" alt="2026-07-12_19-23_2" src="https://github.com/user-attachments/assets/553d036c-6a1a-469e-aebc-928a76cdafe0" />

<img width="3392" height="1772" alt="2026-07-12_19-24" src="https://github.com/user-attachments/assets/b609318d-33b5-4ea8-bba5-7f6247824ebf" />


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

