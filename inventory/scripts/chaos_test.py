
import threading
import requests
import time
import os
import django
import sys
from django.db import transaction

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

# ---------------- Config ----------------
TOTAL_PURCHASES = 50
INITIAL_STOCK = 5

succeeded = 0
failed = 0
lock = threading.Lock()

# ---------------- Seed DB ----------------
Product.objects.filter(name='Test Product').delete()

product = Product.objects.create(
    name='Test Product',
    total_stock=5,
    available_stock=5,
    reserved_stock=0
)


print(f"Seeded product '{product.name}' with total_stock={product.total_stock}")

# ---------------- Purchase Attempt ----------------
def purchase_attempt(product_id):
    global succeeded, failed
    try:
        with transaction.atomic():  # ensures row-level lock
            p = Product.objects.select_for_update().get(id=product_id)
            if p.available_stock > 0:
                p.available_stock -= 1
                p.reserved_stock += 1
                p.save()
                with lock:
                    succeeded += 1
            else:
                with lock:
                    failed += 1
    except Exception as e:
        with lock:
            failed += 1
        print("Exception:", e)

# ---------------- Run 50 Threads ----------------
threads = []

for _ in range(TOTAL_PURCHASES):
    t = threading.Thread(target=purchase_attempt, args=(product.id,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# ---------------- Final Results ----------------
final_product = Product.objects.get(id=product.id)

print("\n=== Chaos Test Results ===")
print(f"Succeeded purchases: {succeeded}")
print(f"Failed purchases: {failed}")
print(f"Final available_stock: {final_product.available_stock}")
print(f"Final reserved_stock: {final_product.reserved_stock}")
print(f"Total stock: {final_product.total_stock}")
