from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models.orders import Order
from inventory.order_states import validate_transition

User = get_user_model()

class OrderStateMachineTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='pass')
        
        self.order = Order.objects.create(user=self.user, total_amount=100.00)
    

    def test_valid_transitions(self):
        # pending → confirmed
        self.order.transition_to('confirmed')
        self.assertEqual(self.order.status, 'confirmed')

        # confirmed → processing
        self.order.transition_to('processing')
        self.assertEqual(self.order.status, 'processing')

    def test_invalid_transition_pending_to_shipped(self):
        order = Order.objects.create(user=self.user, total_amount=50.0)
        with self.assertRaises(ValueError):
            order.transition_to('shipped')

    def test_invalid_transition_shipped_to_cancelled(self):
        order = Order.objects.create(user=self.user, total_amount=50.0, status='shipped')
        with self.assertRaises(ValueError):
            order.transition_to('cancelled')

    def test_delivered_is_immutable(self):
        order = Order.objects.create(user=self.user, total_amount=50.0, status='delivered')
        with self.assertRaises(ValueError):
            order.transition_to('pending')

    def test_cancel_from_pending_or_confirmed(self):
        order = Order.objects.create(user=self.user, total_amount=50.0, status='pending')
        order.transition_to('cancelled')
        self.assertEqual(order.status, 'cancelled')

        order2 = Order.objects.create(user=self.user, total_amount=50.0, status='confirmed')
        order2.transition_to('cancelled')
        self.assertEqual(order2.status, 'cancelled')
