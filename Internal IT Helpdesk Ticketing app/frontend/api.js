var BASE = "http://localhost:8000";

async function request(path, userId, options = {}) {
  const res = await fetch(BASE + path, {
    ...options,
    headers: { "Content-Type": "application/json", "X-User-Id": userId },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

function getUsers() {
  return fetch(BASE + "/users").then((r) => r.json());
}

function getTickets(userId) {
  return request("/tickets", userId);
}

function setStatus(userId, ticketId, status) {
  return request(`/tickets/${ticketId}`, userId, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

function setAssignee(userId, ticketId, assignee) {
  return request(`/tickets/${ticketId}/assignee`, userId, {
    method: "PATCH",
    body: JSON.stringify({ assignee }),
  });
}