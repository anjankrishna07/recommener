import { ItemCard } from "./ItemCard";

function Section({ title, emoji, items, type }) {
  return (
    <div>
      <h2 style={{
        fontFamily: "var(--font-disp)",
        fontSize: "1.5rem",
        marginBottom: 20,
        display: "flex", alignItems: "center", gap: 10,
        color: "var(--text)",
      }}>
        <span>{emoji}</span>
        {title}
        <span style={{
          fontSize: 12, fontFamily: "var(--font-body)",
          color: "var(--muted)", fontWeight: 400,
          background: "rgba(255,255,255,0.05)",
          padding: "2px 10px", borderRadius: 20,
        }}>
          {items.length} results
        </span>
      </h2>
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: 16,
      }}>
        {items.map((item, i) => (
          <ItemCard key={`${type}-${i}`} item={item} type={type} index={i} />
        ))}
      </div>
    </div>
  );
}

export function ResultsGrid({ data }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 48 }}>
      <div style={{
        padding: "12px 20px",
        background: "rgba(94,227,161,0.06)",
        border: "1px solid rgba(94,227,161,0.15)",
        borderRadius: 10,
        fontSize: 13, color: "rgba(94,227,161,0.8)",
        fontFamily: "var(--font-body)",
      }}>
        Results for: <strong>"{data.query}"</strong>
        <span style={{ color: "var(--muted)", marginLeft: 12 }}>
          Hybrid model · 60% content-based TF-IDF + 40% collaborative SVD
        </span>
      </div>

      <Section title="Movies"  emoji="🎬" items={data.movies} type="movie" />
      <Section title="Books"   emoji="📖" items={data.books}  type="book"  />
    </div>
  );
}
