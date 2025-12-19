Inventory Reservation & Order Management System (Django)

Overview
This project implements a strict inventory reservation system, order state machine, concurrency safety guarantees, audit logging, and performance-optimized order queries using Django.
The system is designed to be safe under high concurrency, traceable, and operationally realistic (cleanup, crash recovery, and observability included).


Tech Stack


1. Python 3.9+
2. Django
3. sqlite3
4. PostgreSQL (recommended for row-level locking)
5. Django ORM transactions
6. UUID-based request tracing



How to Run

python -m venv venv
venv\Scripts\activate
pip install requirements/dev.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

python manage.py test inventory.tests.test_order_state_machine
python inventory/scripts/chaos_test.py

celery -A softake worker -l info -P solo
celery -A softake beat -l info

pytest


Global API Rule
✅ Every API response includes a request_id (UUID) for distributed tracing.
Example:
{
  "request_id": "ea675a51dd2b2b5d111c21efe397195638ca6f6b",
  "data": {...}
}


Task 1: Inventory Reservation System

Data Model

from inventory.models.products import Products

Product

total_stock
available_stock
reserved_stock

Invariant (Always Enforced)
available_stock + reserved_stock = total_stock

This invariant is enforced inside database transactions only.



Reservation Rules


POST /api/reservations/

Reservation TTL: 10 minutes


Uses:

transaction.atomic
select_for_update() row-level locking

Why DB Locking?

1. Prevents race conditions
2. Ensures stock never goes negative
3. Guarantees correctness under concurrency



Expiration & Cleanup Strategy

Implemented Method: 

A)Celery beat  

Command:

celery -A softake worker -l info -P solo
celery -A softake beat -l info

What it does:

1. Finds expired reservations
2. Releases reserved stock
3. Restores available stock

Frequency rationale:

1. TTL = 10 minutes
2. Cleanup every 1–2 minutes balances freshness vs DB load


Acceptance Guarantees
✅ Available stock never goes negative
✅ Expired reservations auto-release
✅ Safe under concurrent access


Task 2: Order State Machine (No If-Else Jungle)

how to run

python manage.py test inventory.tests.test_order_state_machine

model data

from inventory.models.orders import Order

Transition Map

TRANSITION_MAP = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['shipped'],
        'shipped': ['delivered'],
        'delivered': [],
        'cancelled': [],
    }

Rules:

1. delivered is immutable
2. shipped → cancelled is forbidden
3. Invalid transitions raise a validation error


Implementation:

1. Dict-based transition map
2. Single validation function
3. No nested if/else chains


Tests
✅ Valid transitions
✅ Invalid transitions
✅ Immutable state enforcement

Task 3: Concurrency Chaos Test

How to run

python inventory/scripts/chaos_test.py


Test Implementation
Implemented using threading inside Django test suite.
Output example:
Succeeded: 5
Failed: 45
Final available_stock: 0
Final reserved_stock: 5

This demonstrates:

1. Fire 50 parallel purchase attempts
2. total_stock = 5, avalable_stock = 5, reserved_stock = 0
3. Expected Result: exactly 5 succeed, 45 fail
4. Stock remains consistent
5. Correct locking
6. No overselling
7. Deterministic behavior under chaos



Task 4: Performance Optimization
Endpoint
GET [/api/orders/]
url = (http://127.0.0.1:8000/api/orders/)

Features

Filters: date range, status, min/max total

Sorting: newest, highest value, Cursor pagination

Indexes Added (PostgreSQL)

CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_total ON orders(total_amount);

Why These Indexes Help

1. created_at → supports pagination + sorting
2. status → fast filtering
3. total_amount → range queries without full scans
4. ORM Optimization
5. select_related() for: user
6. prefetch_related() for: order_items


This avoids:

1. N+1 queries
2. Redundant DB hits
3. Query count reduced from ~12 → 3 per request

Task 5: Audit Log (Explicit, No Signals Abuse)

Audit Log Fields

1. actor
2. action
3. object_type
4. object_id
5. old_value (JSON)
6. new_value (JSON)
7. timestamp

Design Choice
Audit logging is explicitly called from service layer, not hidden behind signals.

Reason:

1. Predictable
2. Easier to test
3. No hidden side effects



Logged Events
✅ Reservation created
✅ Reservation expired
✅ Order created
✅ Order status changed
✅ Stock adjusted

Task 6: Design Questions (Trade-offs)

1. Crash Recovery After Reservation
Problem:

App crashes after reserving stock but before order confirmation

Solution:

Reservations have TTL
Cleanup command reclaims stock
Invariant guarantees consistency after recovery
Trade-off:
Slight delay before stock becomes available again

2. Cleanup Strategy & Frequency


Strategy: management command via cron

Frequency: every 1–2 minutes

Trade-off:

More frequent = fresher stock

Less frequent = lower DB load


3. Multi-Warehouse Design
Option A (Chosen):


Stock(product, warehouse, available, reserved)

Advantages:

Fine-grained control
Supports partial fulfillment

Trade-off:
More complex queries

4. Caching Strategy

Cache:

Product availability (read-heavy)
Order list queries (short TTL)

Where:

Redis
Invalidation:
On stock change
On order state change

Trade-off:

Strong consistency preferred over aggressive caching



System Flow Diagram (Text-Based)
[Reserve Request]
        |
        v
[DB Lock + Atomic Transaction]
        |
        v
[Reservation Created]
        |
        v
[Audit Log Written]
        |
        v
[Order Confirmed]
        |
        v
[Stock Deducted]
        |
        v
[Final Audit Log]


Tests


Total tests: 10+


Coverage includes:


concurrency


invalid state transitions


reservation expiration


audit logging



✅ All tests pass:
python manage.py test


Final Notes
This system prioritizes:

Correctness over shortcuts

Explicit behavior over magic

Operational realism over toy examples


Designed to survive real-world concurrency, failures, and growth.

Submission Completes