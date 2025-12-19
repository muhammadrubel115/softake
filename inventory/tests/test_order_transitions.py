import pytest
from django.contrib.auth import get_user_model
from inventory.models import Order
from inventory.order_states import InvalidOrderTransition

User = get_user_model()

@pytest.mark.django_db
def test_cannot_cancel_after_shipped():
    user = User.objects.create_user(email='a@test.com', password='pass')

    order = Order.objects.create(
        user=user,
        status=Order.STATUS_SHIPPED,
        total_amount=100
    )

    with pytest.raises(InvalidOrderTransition):
        order.transition_to(Order.STATUS_CANCELLED)

@pytest.mark.django_db
def test_delivered_is_immutable():
    user = User.objects.create_user(email='b@test.com', password='pass')

    order = Order.objects.create(
        user=user,
        status=Order.STATUS_DELIVERED,
        total_amount=200
    )

    with pytest.raises(InvalidOrderTransition):
        order.transition_to(Order.STATUS_PROCESSING)


@pytest.mark.django_db
def test_cannot_skip_states():
    user = User.objects.create_user(email='c@test.com', password='pass')

    order = Order.objects.create(
        user=user,
        status=Order.STATUS_PENDING,
        total_amount=300
    )

    with pytest.raises(InvalidOrderTransition):
        order.transition_to(Order.STATUS_SHIPPED)


@pytest.mark.django_db
def test_valid_transition_pending_to_confirmed():
    user = User.objects.create_user(email='d@test.com', password='pass')

    order = Order.objects.create(
        user=user,
        status=Order.STATUS_PENDING,
        total_amount=400
    )

    order.transition_to(Order.STATUS_CONFIRMED)

    order.refresh_from_db()
    assert order.status == Order.STATUS_CONFIRMED
