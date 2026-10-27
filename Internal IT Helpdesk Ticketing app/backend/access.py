STAFF_ROLES = ("agent", "admin")


def is_staff(user: dict) -> bool:
    return user["role"] in STAFF_ROLES


def is_admin(user: dict) -> bool:
    return user["role"] == "admin"


def can_view(user: dict, ticket: dict) -> bool:
    return is_staff(user) or ticket["requester"] == user["id"]


def visible_tickets(user: dict, tickets: list[dict]) -> list[dict]:
    return [t for t in tickets if can_view(user, t)]