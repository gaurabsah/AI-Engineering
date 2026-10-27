import json
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from access import can_view, is_admin, is_staff, visible_tickets

DATA = Path(__file__).parent / "data"
USERS = {u["id"]: u for u in json.loads((DATA / "users.json").read_text())}
TICKETS = {t["id"]: t for t in json.loads((DATA / "tickets.json").read_text())}

app = FastAPI(title="Helpdesk")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


def current_user(x_user_id: str | None = Header(default=None)) -> dict:
    # Fake auth: the UI sends the selected user's id in a header.
    if x_user_id not in USERS:
        raise HTTPException(401, "Unknown or missing X-User-Id")
    return USERS[x_user_id]


def get_ticket_for(user: dict, ticket_id: int) -> dict:
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        raise HTTPException(404, "Ticket not found")
    if not can_view(user, ticket):
        raise HTTPException(403, "Not allowed")
    return ticket


@app.get("/users")
def list_users():
    # Needed only to populate the user-switcher dropdown.
    return list(USERS.values())


class RoleUpdate(BaseModel):
    role: Literal["employee", "agent", "admin"]


@app.patch("/users/{user_id}")
def update_role(user_id: str, body: RoleUpdate, user: dict = Depends(current_user)):
    if not is_admin(user):
        raise HTTPException(403, "Only admins can change roles")
    target = USERS.get(user_id)
    if target is None:
        raise HTTPException(404, "User not found")
    if target["id"] == user["id"]:
        raise HTTPException(422, "Admins cannot change their own role")
    target["role"] = body.role
    return target


@app.get("/tickets")
def list_tickets(user: dict = Depends(current_user)):
    return visible_tickets(user, list(TICKETS.values()))


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, user: dict = Depends(current_user)):
    return get_ticket_for(user, ticket_id)


class StatusUpdate(BaseModel):
    status: Literal["open", "in_progress", "resolved"]


@app.patch("/tickets/{ticket_id}")
def update_status(ticket_id: int, body: StatusUpdate, user: dict = Depends(current_user)):
    ticket = get_ticket_for(user, ticket_id)
    if not is_staff(user):
        raise HTTPException(403, "Only agents and admins can change status")
    ticket["status"] = body.status
    return ticket


class Reassign(BaseModel):
    assignee: str | None  # a staff user id, or null to unassign


@app.patch("/tickets/{ticket_id}/assignee")
def reassign(ticket_id: int, body: Reassign, user: dict = Depends(current_user)):
    ticket = get_ticket_for(user, ticket_id)
    if not is_admin(user):
        raise HTTPException(403, "Only admins can reassign tickets")
    if body.assignee is not None:
        target = USERS.get(body.assignee)
        if target is None or not is_staff(target):
            raise HTTPException(422, "Assignee must be an agent or admin")
    ticket["assignee"] = body.assignee
    return ticket