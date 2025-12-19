# inventory/tests/test_order_state_machine.py
from django.test import TestCase
from django.contrib.auth import get_user_model
 # works after step 2
from inventory.order_states import validate_transition
from .orders import Order
