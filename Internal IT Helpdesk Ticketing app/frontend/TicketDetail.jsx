var STATUSES = ["open", "in_progress", "resolved"];

function statusLabel(s) {
  return s.replace("_", " ");
}

function TicketDetail({ ticket, user, users, onUpdate }) {
  const [error, setError] = React.useState("");

  // UI hints only. The backend enforces these rules.
  const isStaff = user.role === "agent" || user.role === "admin";
  const isAdmin = user.role === "admin";

  const nameOf = (id) => users.find((u) => u.id === id)?.name ?? id;

  async function change(call) {
    setError("");
    try {
      onUpdate(await call());
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="detail">
      <h2>#{ticket.id} {ticket.title}</h2>
      <p className="meta">
        {ticket.category} · requested by {nameOf(ticket.requester)}
      </p>
      <p>{ticket.description}</p>

      <dl>
        <dt>Priority</dt>
        <dd>{ticket.priority}</dd>

        <dt>Status</dt>
        <dd>
          {isStaff ? (
            <select
              value={ticket.status}
              onChange={(e) => change(() => setStatus(user.id, ticket.id, e.target.value))}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>{statusLabel(s)}</option>
              ))}
            </select>
          ) : (
            statusLabel(ticket.status)
          )}
        </dd>

        <dt>Assignee</dt>
        <dd>
          {isAdmin ? (
            <select
              value={ticket.assignee ?? ""}
              onChange={(e) =>
                change(() => setAssignee(user.id, ticket.id, e.target.value || null))
              }
            >
              <option value="">Unassigned</option>
              {users
                .filter((u) => u.role !== "employee")
                .map((u) => (
                  <option key={u.id} value={u.id}>{u.name}</option>
                ))}
            </select>
          ) : ticket.assignee ? (
            nameOf(ticket.assignee)
          ) : (
            "Unassigned"
          )}
        </dd>
      </dl>

      {error && <p className="error">{error}</p>}

      <h3>Comments</h3>
      {ticket.comments.length === 0 ? (
        <p className="empty">No comments yet.</p>
      ) : (
        <ul className="comments">
          {ticket.comments.map((c, i) => (
            <li key={i}>
              <strong>{nameOf(c.author)}:</strong> {c.text}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}