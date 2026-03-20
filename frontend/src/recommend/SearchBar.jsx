import { useState } from "react";

const SUGGESTIONS = [
  "space exploration and alien civilisations",
  "psychological thriller with twist endings",
  "romantic comedy set in Europe",
  "survival in the wilderness",
  "artificial intelligence and ethics",
  "historical war drama",
  "heist and crime mystery",
  "coming of age stories",
];

export function SearchBar({ onSearch, loading }) {
  const [query, setQuery]   = useState("");
  const [focused, setFocused] = useState(false);

  const submit = () => {
    const q = query.trim();
    if (q.length >= 2) onSearch(q);
  };

  return (
    <div style={{ width: "100%", maxWidth: 680, margin: "0 auto" }}>
      <div style={{
        display: "flex",
        border: `1.5px solid ${focused ? "rgba(200,169,110,0.5)" : "var(--border)"}`,
        borderRadius: 12,
        background: "var(--surface)",
        overflow: "hidden",
        transition: "border-color 0.2s",
        boxShadow: focused ? "0 0 0 3px rgba(200,169,110,0.08)" : "none",
      }}>
        <span style={{ padding: "14px 16px", fontSize: 18, color: "var(--muted)" }}>🔍</span>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          onKeyDown={e => e.key === "Enter" && submit()}
          placeholder="Describe what you're in the mood for…"
          style={{
            flex: 1, background: "none", border: "none", outline: "none",
            color: "var(--text)", fontSize: "1rem", fontFamily: "var(--font-body)",
          }}
        />
        <button
          onClick={submit}
          disabled={loading || query.trim().length < 2}
          style={{
            padding: "14px 24px",
            background: loading ? "rgba(200,169,110,0.3)" : "var(--accent)",
            border: "none", color: "#0a0a0f",
            fontFamily: "var(--font-body)", fontWeight: 600,
            fontSize: "0.9rem", cursor: "pointer",
            opacity: query.trim().length < 2 ? 0.4 : 1,
            transition: "opacity 0.2s, background 0.2s",
          }}
        >
          {loading ? (
            <span style={{
              display: "inline-block", width: 16, height: 16,
              border: "2px solid #0a0a0f", borderTopColor: "transparent",
              borderRadius: "50%", animation: "spin 0.7s linear infinite",
            }} />
          ) : "Discover"}
        </button>
      </div>

      {/* Suggestion chips */}
      <div style={{ marginTop: 16, display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
        {SUGGESTIONS.slice(0, 5).map(s => (
          <button
            key={s}
            onClick={() => { setQuery(s); onSearch(s); }}
            style={{
              background: "rgba(255,255,255,0.04)",
              border: "1px solid var(--border)",
              borderRadius: 20, padding: "5px 13px",
              fontSize: 12, color: "var(--muted)",
              cursor: "pointer", fontFamily: "var(--font-body)",
              transition: "color 0.2s, border-color 0.2s",
            }}
            onMouseEnter={e => { e.target.style.color = "var(--text)"; e.target.style.borderColor = "rgba(255,255,255,0.2)"; }}
            onMouseLeave={e => { e.target.style.color = "var(--muted)"; e.target.style.borderColor = "var(--border)"; }}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
