function TicketList({ tickets, selectedId, onSelect }) {
  if (tickets.length === 0) return <p className="empty">No tickets.</p>;

  return (
    <ul className="ticket-list">
      {tickets.map((t) => (
        <li key={t.id} className={t.id === selectedId ? "selected" : ""}>
          <button onClick={() => onSelect(t.id)}>
            <div>#{t.id} {t.title}</div>
            <div>
              <span className={`badge ${t.status}`}>{t.status.replace("_", " ")}</span>
              <span className={`badge ${t.priority}`}>{t.priority}</span>
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}