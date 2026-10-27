var ROLES = ["employee", "agent", "admin"];

function App() {
  const [users, setUsers] = React.useState([]);
  const [userId, setUserId] = React.useState("");
  const [tickets, setTickets] = React.useState([]);
  const [selectedId, setSelectedId] = React.useState(null);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    getUsers()
      .then((list) => {
        setUsers(list);
        setUserId(list[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  React.useEffect(() => {
    if (!userId) return;
    let ignore = false; // drop stale responses when switching users quickly
    setSelectedId(null);
    setError("");
    getTickets(userId)
      .then((list) => !ignore && setTickets(list))
      .catch((e) => !ignore && setError(e.message));
    return () => { ignore = true; };
  }, [userId]);

  const user = users.find((u) => u.id === userId);
  const selected = tickets.find((t) => t.id === selectedId);

  const replaceTicket = (updated) =>
    setTickets((list) => list.map((t) => (t.id === updated.id ? updated : t)));

  return (
    <div className="app">
      <header>
        <h1>IT Helpdesk</h1>
        <label>
          Signed in as{" "}
          <select value={userId} onChange={(e) => setUserId(e.target.value)}>
            {ROLES.map((role) => (
              <optgroup key={role} label={role}>
                {users
                  .filter((u) => u.role === role)
                  .map((u) => (
                    <option key={u.id} value={u.id}>{u.name}</option>
                  ))}
              </optgroup>
            ))}
          </select>
        </label>
      </header>

      {error && <p className="error banner">{error}</p>}

      <div className="main">
        <aside className="sidebar">
          <TicketList tickets={tickets} selectedId={selectedId} onSelect={setSelectedId} />
        </aside>
        <section className="content">
          {selected && user ? (
            <TicketDetail
              key={selected.id}
              ticket={selected}
              user={user}
              users={users}
              onUpdate={replaceTicket}
            />
          ) : (
            <p className="empty">Select a ticket.</p>
          )}
        </section>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);