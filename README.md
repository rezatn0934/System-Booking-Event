# Event Booking System

A backend service built with **Django** and **Django REST Framework**
for managing events and ticket reservations.

The system guarantees that event capacity is never exceeded, even under
concurrent booking requests, while providing a reliable reservation
expiration mechanism.

------------------------------------------------------------------------

# Tech Stack

-   Python 3.13
-   Django
-   Django REST Framework
-   PostgreSQL
-   Redis
-   RabbitMQ
-   Celery
-   JWT Authentication
-   Docker & Docker Compose

------------------------------------------------------------------------

# Features

## Authentication

-   OTP login using Redis (OTP codes are never stored in the database)
-   Optional password authentication
-   JWT access & refresh tokens
-   Logout with token invalidation
-   User profile endpoint

## Events

-   Create, update and delete events (Admin only)
-   Public event list and detail
-   Search, filtering, ordering and pagination
-   Event statistics:
    -   Total capacity
    -   Active bookings (Pending + Confirmed)
    -   Confirmed bookings
    -   Remaining capacity

## Bookings

-   Create booking
-   Confirm booking (payment simulation)
-   Cancel booking
-   List and retrieve bookings

Business rules:

-   One active booking per user per event
-   Capacity is never exceeded
-   New bookings are created as **PENDING**
-   Pending bookings expire after 10 minutes
-   Expired bookings automatically release capacity

------------------------------------------------------------------------

# Project Structure

``` text
accounts/
    authentication/
    serializers/
    services/
    views/

bookings/
    models/
    selectors/
    serializers/
    services/
    states/
    tasks/
    views/

config/
tests/
```

------------------------------------------------------------------------

# Running the Project

## Clone

``` bash
git clone <repository-url>
cd event-booking
```

## Environment Variables

Create a `.env` file.

``` env
SECRET_KEY=your-secret-key

DEBUG=True

POSTGRES_DB=event_booking
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

## Docker

``` bash
docker compose up --build
```

## Migrations

``` bash
python manage.py migrate
```

## Create Superuser

``` bash
python manage.py createsuperuser
```

## Run Django

``` bash
python manage.py runserver
```

## Run Celery Worker

``` bash
celery -A config worker -l info
```

## Run Celery Beat

``` bash
celery -A config beat -l info
```

------------------------------------------------------------------------

# Architecture

The project follows a layered architecture:

``` text
Request
   │
   ▼
Views
   │
   ▼
Serializers
   │
   ▼
Services
   │
   ▼
Selectors
   │
   ▼
Models / Database
```

Responsibilities:

-   **Views**: HTTP layer only.
-   **Serializers**: Validation and serialization.
-   **Services**: Business logic and transaction management.
-   **Selectors**: Optimized read queries.
-   **Models**: Database schema and constraints.

------------------------------------------------------------------------

# Concurrency Strategy

Overselling prevention is the highest priority.

The implementation combines multiple protection layers:

## Pessimistic Locking

The event row is locked using:

``` python
Event.objects.select_for_update()
```

Only one transaction can reserve seats for the same event at a time.

## Database Constraints

A partial unique constraint prevents duplicate active bookings.

``` text
(event, user)
WHERE status IN (PENDING, CONFIRMED)
```

## Atomic Transactions

Critical operations execute inside:

``` python
transaction.atomic()
```

## Idempotency

Repeated booking requests return the existing active booking instead of
creating duplicates.

------------------------------------------------------------------------

# Reservation Expiration

Each booking is created with:

-   Status = `PENDING`
-   `expires_at = now + 10 minutes`

After the transaction is committed:

``` python
transaction.on_commit(...)
```

A Celery task is scheduled using ETA.

When the task executes it:

1.  Locks the booking row.
2.  Validates the current state.
3.  Expires the booking if it is still pending.

The process is retry-safe and idempotent.

------------------------------------------------------------------------

# State Pattern

Booking lifecycle:

``` text
PENDING
 ├──► CONFIRMED
 ├──► CANCELED
 └──► EXPIRED
```

Each state encapsulates its own transition rules, improving
maintainability and extensibility.

------------------------------------------------------------------------

# Design Decisions

## Redis for OTP

OTP codes are temporary and should not be persisted in PostgreSQL.

## Service Layer

Business logic is reusable from REST APIs, Celery tasks and management
commands.

## Selector Layer

Selectors isolate read queries and keep services focused on business
logic.

## Pessimistic Locking

Correctness and consistency are prioritized over maximum throughput.

------------------------------------------------------------------------

# Trade-offs

Chosen:

-   Pessimistic locking
-   Service layer
-   State pattern
-   Redis for OTP
-   Celery for asynchronous expiration

Advantages:

-   Prevents overselling
-   High consistency
-   Reliable expiration
-   Maintainable architecture

Disadvantages:

-   Reduced concurrency under extreme load due to row locking.
-   Extra infrastructure (Redis, RabbitMQ, Celery).

------------------------------------------------------------------------

# Future Improvements

-   Payment gateway integration
-   Waiting list support
-   Notification service
-   Rate limiting
-   Event-driven architecture
-   Distributed locking

------------------------------------------------------------------------

# License

Implemented as part of a Senior Backend Engineering challenge.
