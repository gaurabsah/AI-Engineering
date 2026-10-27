import json
from pathlib import Path

from access import can_view, visible_tickets

DATA = Path(__file__).parent.parent / "data"
USERS = {u["id"]: u for u in json.loads((DATA / "users.json").read_text())}
TICKETS = json.loads((DATA / "tickets.json").read_text())


def test_employee_sees_only_own_tickets():
    visible = visible_tickets(USERS["u1"], TICKETS)
    assert visible
    assert all(t["requester"] == "u1" for t in visible)


def test_employee_cannot_view_others_ticket():
    other = next(t for t in TICKETS if t["requester"] != "u1")
    assert not can_view(USERS["u1"], other)


def test_agent_sees_all_tickets():
    assert len(visible_tickets(USERS["a1"], TICKETS)) == len(TICKETS)


def test_admin_sees_all_tickets():
    assert len(visible_tickets(USERS["ad1"], TICKETS)) == len(TICKETS)