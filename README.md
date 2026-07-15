# Event Booking System

A production-oriented backend service built with **Django** and **Django REST Framework** for managing events and reservations.

The project focuses on correctness, consistency, and reliability under concurrent booking requests. It guarantees that event capacity is never exceeded while providing an asynchronous and fault-tolerant reservation expiration mechanism.

---

# Table of Contents

- Features
- Tech Stack
- Architecture
- Project Structure
- Running the Project
- API Overview
- Authentication
- Booking Workflow
- Concurrency Strategy
- Reservation Expiration
- State Pattern
- Security
- Reliability
- Design Decisions
- Trade-offs
- Future Improvements

---

# Features

## Authentication

- OTP authentication using Redis
- IP-based OTP abuse protection
- Optional password authentication
- JWT Access & Refresh Tokens
- Logout with token invalidation
- User profile endpoint

---

## Event Management

- Public event list
- Public event detail
- Admin-only event creation
- Admin-only event update
- Admin-only event deletion
- Pagination
- Search
- Filtering
- Ordering

Event statistics include:

- Total Capacity
- Active Reservations
- Confirmed Reservations
- Remaining Capacity

Event deletion protection:

- Started events cannot be deleted.
- Events with active reservations cannot be deleted.

---

## Booking Management

- Create reservation
- Confirm reservation
- Cancel reservation
- List reservations
- Retrieve reservation

Business Rules

- Every reservation starts as **PENDING**
- Reservation expires after **10 minutes**
- Expired reservations automatically release capacity
- One active reservation per user per event
- Capacity is never exceeded
- Reservation creation is idempotent
- Confirmation is allowed only before the event starts
- Cancellation is allowed only before the event starts

---

# Tech Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.13 |
| Framework | Django |
| API | Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis |
| Message Broker | RabbitMQ |
| Background Jobs | Celery |
| Web Server | Gunicorn |
| Reverse Proxy | Nginx |
| Authentication | JWT |
| Containerization | Docker |

---

# Architecture

The project follows a layered architecture to separate concerns and keep business logic independent from the HTTP layer.

```text
                HTTP Request
                     │
                     ▼
              Django REST Framework
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
    Permissions              Serializers
                                   │
                                   ▼
                              Services
                           ┌─────┴─────┐
                           ▼           ▼
                      Selectors    Celery Tasks
                           │           │
                           └─────┬─────┘
                                 ▼
                           PostgreSQL

Redis (OTP Storage)
RabbitMQ (Broker)
```

Layer responsibilities

### Views

- HTTP endpoints
- Authentication
- Permissions
- Calling services

### Serializers

- Validation
- Serialization
- Request parsing

### Services

- Business logic
- Transaction management
- Coordination between models

### Selectors

- Read-only optimized queries
- Query composition
- Statistics

### Models

- Database schema
- Constraints
- Relationships

---

# Project Structure

```text
.
├── accounts
│   ├── management/
│   │   └── commands/
│   ├── services/
│   ├── admin.py
│   ├── authenticators.py
│   ├── exceptions.py
│   ├── managers.py
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── urls.py
│   ├── utils.py
│   ├── validators.py
│   └── views.py
│
├── bookings
│   ├── migrations/
│   ├── selectors/
│   ├── serializers/
│   ├── services/
│   ├── states/
│   ├── views/
│   ├── admin.py
│   ├── exceptions.py
│   ├── models.py
│   ├── tasks.py
│   ├── urls.py
│   └── tests.py
│
├── config
│   ├── base_task.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── env
│   ├── postgres.env
│   ├── postgres.env.example
│   ├── rabbitmq.env
│   └── rabbitmq.env.example
│
├── static/
├── docker-compose.yml
├── Dockerfile
├── Dockerfile-Nginx
├── nginx.conf
├── init.sh
├── wait-for-it.sh
├── manage.py
├── pyproject.toml
├── uv.lock
├── LICENSE
└── README.md
```
## Directory Overview

| Directory | Responsibility |
|-----------|----------------|
| `accounts/` | Authentication, OTP workflow, JWT, user management |
| `bookings/` | Event and reservation domain, business rules, state management |
| `config/` | Django settings, Celery configuration, base task definitions |
| `env/` | Environment configuration templates |
| `static/` | Static files |
| `init.sh` | Container initialization (migrations, collectstatic, startup) |
| `wait-for-it.sh` | Waits for dependent services before application startup |
| `Dockerfile` | Django application image |
| `Dockerfile-Nginx` | Nginx image |
| `docker-compose.yml` | Local development orchestration |
| `nginx.conf` | Reverse proxy configuration |
---

# Running the Project

## Clone

```bash
git clone <repository-url>

cd event-booking
```

## Configure Environment

Create a `.env` file.

Example:

```env
SECRET_KEY=change-me

DEBUG=True

ENGINE=event_booking
DBNAME=postgres
DBUSER=postgres
DBPASSWORD=postgres
DBHOST=db
DBPORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

DEFAULT_CACHE_DATABASE=3
DEFAULT_CACHE_TTL=3600

OTP_CACHE_DATABASE=6
OTP_CACHE_TTL=300

SUPERUSER=09123456789
SUPERPASS=admin

```

## Start

```bash
docker compose up --build
```

## Apply Migrations

```bash
docker compose exec app python manage.py migrate
```

## API Documentation

The API is available after starting the application.
# API Overview

## Authentication

| Method | Endpoint | Description |
|----------|----------------|----------------|
| POST | `/api/v1/auth/send-otp/` | Send OTP |
| POST | `/api/v1/auth/verify-otp/` | Verify OTP |
| POST | `/api/v1/auth/login/` | Login with password |
| POST | `/api/v1/auth/refresh/` | Refresh JWT |
| POST | `/api/v1/auth/logout/` | Logout |
| GET | `/api/v1/auth/profile/` | Current user |

---

## Events

| Method | Endpoint | Permission |
|----------|----------------|----------------|
| GET | `/api/v1/events/` | Public |
| GET | `/api/v1/events/{id}/` | Public |
| POST | `/api/v1/events/` | Admin |
| PATCH | `/api/v1/events/{id}/` | Admin |
| DELETE | `/api/v1/events/{id}/` | Admin |

Supported query parameters:

```
search=
ordering=
page=
event_date=
```

---

## Bookings

| Method | Endpoint |
|----------|----------------|
| GET | `/api/v1/bookings/` |
| GET | `/api/v1/bookings/{id}/` |
| POST | `/api/v1/bookings/` |
| POST | `/api/v1/bookings/{id}/confirm/` |
| POST | `/api/v1/bookings/{id}/cancel/` |

Filtering

```
status=
event=
user=
```

Ordering

```
created_at
confirmed_at
expires_at
status
event__event_date
```

Search

```
event__title
```

---

# Booking Workflow

```text
Create Reservation
        │
        ▼
     PENDING
        │
        ├──────────────┐
        ▼              ▼
 Confirmed        10 Minutes Passed
                        │
                        ▼
                    EXPIRED
```

Users may also cancel reservations before the event starts.

---

# Concurrency Strategy

Overselling prevention is the primary design goal.

Multiple protection layers are implemented.

## 1. Atomic Transactions

Every critical operation executes inside:

```python
transaction.atomic()
```

This guarantees consistency throughout the booking lifecycle.

---

## 2. Row-Level Locking

The corresponding event row is locked during booking creation.

```python
Event.objects.select_for_update()
```

Only one transaction can modify the available capacity for a specific event at a time.

---

## 3. Database Constraints

A partial unique constraint prevents duplicate active reservations.

```
(event, user)

WHERE status IN (PENDING, CONFIRMED)
```

Even if two identical requests arrive simultaneously, the database guarantees correctness.

---

## 4. Idempotency

Repeated reservation requests never create duplicate reservations.

If an active reservation already exists, it is returned instead of creating another one.

---

## 5. Reliable Task Scheduling

Reservation expiration tasks are scheduled only after the database transaction has been committed.

```python
transaction.on_commit(...)
```

This prevents orphan background tasks from being published for rolled-back transactions.

---

# Reservation Expiration

Every reservation contains:

```
status = PENDING

expires_at = now + 10 minutes
```

After commit:

```
expire_booking.apply_async(
    eta=booking.expires_at
)
```

The worker executes the expiration task exactly when the reservation expires.

When executed it:

1. Locks the reservation.
2. Checks its current state.
3. Expires it if still pending.
4. Releases event capacity.

---

## Recovery Mechanism

A periodic Celery Beat task periodically scans overdue reservations.

This acts as a recovery layer if:

- Worker was unavailable
- Broker temporarily failed
- ETA task was missed

The periodic task simply re-dispatches expiration tasks.

Since expiration is idempotent, executing it multiple times is safe.

---

# State Pattern

Reservation lifecycle is implemented using the State Pattern.

```text
               +-------------+
               |   PENDING   |
               +-------------+
                /     |     \
               /      |      \
              ▼       ▼       ▼

      CONFIRMED   CANCELED   EXPIRED
```

Each state owns its own transition rules.

Benefits

- Better maintainability
- Open for extension
- Eliminates complex conditional statements
- Easier testing

---

# Celery

Celery is responsible for asynchronous reservation expiration.

Components

- RabbitMQ
- Celery Worker
- Celery Beat

Worker

- Executes ETA tasks
- Retries automatically
- Acknowledges messages only after successful execution

Beat

- Periodically scans overdue reservations
- Provides recovery against missed ETA tasks

# Security

The project applies multiple security layers.

## Authentication

- JWT Access Token
- JWT Refresh Token
- Logout with token invalidation

---

## OTP

OTP codes are **never stored inside PostgreSQL**.

Instead:

- Stored inside Redis
- Short TTL
- Automatically removed after expiration

Benefits

- Faster access
- No unnecessary database writes
- Automatic cleanup

---

## OTP Abuse Protection

To reduce OTP abuse:

- Temporary IP blocking
- Redis counters
- Configurable cooldown period

---

## Authorization

Event management endpoints are restricted to administrators.

Public users can:

- Browse events
- View event details

Authenticated users can:

- Create reservations
- Confirm reservations
- Cancel reservations
- View only their own reservations

Administrators can:

- Manage all events
- View every reservation

---

## DRF Throttling

Rate limiting is enabled to reduce abusive requests.

Anonymous users:

```
100/hour
```

Authenticated users:

```
1000/hour
```

---

## Reverse Proxy

Nginx is used as the reverse proxy.

Responsibilities

- Reverse proxy
- Static file serving
- Request forwarding
- Security headers
- Compression

---

# Reliability

Several mechanisms guarantee system consistency.

## Atomic Transactions

Critical operations execute inside

```python
transaction.atomic()
```

---

## Row-Level Locking

```python
select_for_update()
```

Guarantees that concurrent reservation requests cannot oversell an event.

---

## Retry-safe Tasks

Celery tasks are designed to be retry-safe.

Executing the same expiration task multiple times never corrupts data.

---

## Automatic Recovery

Even if:

- a worker crashes,
- RabbitMQ is temporarily unavailable,
- ETA execution is delayed,

the periodic recovery task eventually expires overdue reservations.

---

## Reliable Task Publishing

Tasks are published only after successful database commits.

```python
transaction.on_commit(...)
```

This guarantees consistency between the database and the message broker.

---

# Design Decisions

## Service Layer

Business logic is intentionally isolated from Views.

Advantages

- Easier testing
- Reusable logic
- Cleaner HTTP layer

---

## Selector Layer

Read operations are isolated from business logic.

Benefits

- Better query optimization
- Easier maintenance
- Clear separation of responsibilities

---

## Redis for OTP

OTP codes are temporary data.

Redis is a better fit than PostgreSQL because:

- In-memory storage
- Built-in expiration
- Higher performance

---

## Pessimistic Locking

The system prioritizes correctness over maximum throughput.

Using

```python
SELECT FOR UPDATE
```

ensures that event capacity is always accurate.

---

## State Pattern

Reservation lifecycle is implemented using the State Pattern.

Instead of large conditional blocks, each state is responsible for its own transitions.

Advantages

- Extensible
- Testable
- Easy to maintain

---

# Trade-offs

The following architectural decisions were intentionally made.

| Decision | Benefit | Cost |
|-----------|---------|------|
| Pessimistic Locking | Prevents overselling | Lower concurrency |
| Service Layer | Clean architecture | More files |
| Selector Layer | Optimized reads | Additional abstraction |
| Redis OTP | Fast temporary storage | Requires Redis |
| Celery | Reliable async jobs | Extra infrastructure |
| RabbitMQ | Durable message broker | Operational complexity |

Overall, consistency and correctness were prioritized over maximum throughput.

---

# Future Improvements

Potential enhancements include:

- Payment gateway integration
- Waiting list support
- Email notifications
- SMS notifications
- Prometheus metrics
- Grafana dashboards
- Distributed tracing
- Outbox Pattern
- Event-driven architecture
- Horizontal worker autoscaling
- Kubernetes deployment
- CI/CD pipeline
- Multi-region deployment

---

# Why This Architecture?

The architecture was designed around four primary goals:

1. **Correctness** — Event capacity must never be exceeded.
2. **Reliability** — Reservation expiration must be fault tolerant.
3. **Maintainability** — Business logic should remain isolated and easy to extend.
4. **Scalability** — Components such as Redis, RabbitMQ, Celery Workers, and the API can be scaled independently.

---
