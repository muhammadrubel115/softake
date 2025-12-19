from django.test import TestCase

# Create your tests here.
# inventory/scripts/chaos_test.py

import threading
import requests
import time
import os
import django
import sys

# ------------------------
# Add project root
# ------------------------
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# ------------------------
# Setup Django
# ------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "softake.settings.dev")
django.setup()

from inventory.models.products import Product

# ------------------------
# Configuration (MANDATORY)
# ------------------------
API_URL = "http://127.0.0.1:8000/api/reservations/"
PRODUCT_ID = 8
ATTEMPTS = 50
QUANTITY = 1

TOKEN = "ea675a51dd2b2b5d111c21efe397195638ca6f6b"
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
}

# ------------------------
# Validate seeded stock (DO NOT MODIFY)
# ------------------------
product = Product.objects.get(id=PRODUCT_ID)

assert product.total_stock == 5, "total_stock must be 5"
assert product.available_stock == 5, "available_stock must be 5"
assert product.reserved_stock == 0, "reserved_stock must be 0"

print("[OK] Stock seeded correctly")

# ------------------------
# Chaos counters
# ------------------------
success = 0
failure = 0
lock = threading.Lock()

# ------------------------
# Attack function
# ------------------------
def attempt_reservation():
    global success, failure

    r = requests.post(
        API_URL,
        json={"product": PRODUCT_ID, "quantity": QUANTITY},
        headers=HEADERS,
        timeout=5,
    )

    with lock:
        if r.status_code == 201:
            success += 1
        else:
            failure += 1

# ------------------------
# Run chaos
# ------------------------
threads = []
start = time.time()

for _ in range(ATTEMPTS):
    t = threading.Thread(target=attempt_reservation)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

elapsed = time.time() - start

# ------------------------
# Final verification
# ------------------------
product.refresh_from_db()

print("\n===== CHAOS TEST RESULT =====")
print(f"Succeeded: {success}")
print(f"Failed: {failure}")
print(f"Total attempts: {ATTEMPTS}")
print(f"Time taken: {elapsed:.2f}s")
print(
    f"Final Stock - available: {product.available_stock}, "
    f"reserved: {product.reserved_stock}, "
    f"total: {product.total_stock}"
)

if success == 5 and product.available_stock == 0 and product.reserved_stock == 5:
    print("[PASS] Concurrency control proven")
else:
    print("[FAIL] Concurrency bug detected")
