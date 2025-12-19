
# inventory/order_states.py

class InvalidOrderTransition(ValueError):
    pass



TRANSITION_MAP = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['processing', 'cancelled'],
    'processing': ['shipped'],
    'shipped': ['delivered'],
    'delivered': [],
    'cancelled': [],
}


def validate_transition(current_status: str, new_status: str):
    allowed = TRANSITION_MAP.get(current_status, [])

    if new_status not in allowed:
        raise InvalidOrderTransition(
            f"Invalid transition from '{current_status}' to '{new_status}'"
        )
