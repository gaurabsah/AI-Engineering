from fastapi.testclient import TestClient

from main import TICKETS, app

client = TestClient(app)


def h(user_id):
    return {"X-User-Id": user_id}


def test_missing_user_is_401():
    assert client.get("/tickets").status_code == 401


def test_employee_list_is_filtered():
    tickets = client.get("/tickets", headers=h("u1")).json()
    assert tickets and all(t["requester"] == "u1" for t in tickets)


def test_agent_list_has_everything():
    assert len(client.get("/tickets", headers=h("a1")).json()) == len(TICKETS)


def test_employee_gets_403_on_others_ticket():
    other_id = next(i for i, t in TICKETS.items() if t["requester"] != "u1")
    assert client.get(f"/tickets/{other_id}", headers=h("u1")).status_code == 403


def test_unknown_ticket_is_404():
    assert client.get("/tickets/9999", headers=h("a1")).status_code == 404


def test_agent_can_change_status():
    r = client.patch("/tickets/1", json={"status": "resolved"}, headers=h("a1"))
    assert r.status_code == 200 and r.json()["status"] == "resolved"


def test_employee_cannot_change_status():
    r = client.patch("/tickets/1", json={"status": "resolved"}, headers=h("u1"))
    assert r.status_code == 403


def test_invalid_status_is_rejected():
    r = client.patch("/tickets/1", json={"status": "banana"}, headers=h("a1"))
    assert r.status_code == 422


def test_admin_can_change_status():
    r = client.patch("/tickets/1", json={"status": "in_progress"}, headers=h("ad1"))
    assert r.status_code == 200


def test_admin_can_reassign():
    r = client.patch("/tickets/1/assignee", json={"assignee": "a2"}, headers=h("ad1"))
    assert r.status_code == 200 and r.json()["assignee"] == "a2"


def test_agent_cannot_reassign():
    r = client.patch("/tickets/1/assignee", json={"assignee": "a2"}, headers=h("a1"))
    assert r.status_code == 403


def test_employee_cannot_reassign():
    r = client.patch("/tickets/1/assignee", json={"assignee": "a2"}, headers=h("u1"))
    assert r.status_code == 403


def test_cannot_assign_to_employee():
    r = client.patch("/tickets/1/assignee", json={"assignee": "u2"}, headers=h("ad1"))
    assert r.status_code == 422


def test_admin_can_change_role():
    r = client.patch("/users/u4", json={"role": "agent"}, headers=h("ad1"))
    assert r.status_code == 200 and r.json()["role"] == "agent"


def test_agent_cannot_change_role():
    r = client.patch("/users/u2", json={"role": "admin"}, headers=h("a1"))
    assert r.status_code == 403


def test_admin_cannot_change_own_role():
    r = client.patch("/users/ad1", json={"role": "employee"}, headers=h("ad1"))
    assert r.status_code == 422


def test_unknown_user_is_404():
    r = client.patch("/users/nope", json={"role": "agent"}, headers=h("ad1"))
    assert r.status_code == 404