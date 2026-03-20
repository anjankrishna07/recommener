import { useState } from "react";
import { ScoreBar } from "./ScoreBar";

const GENRE_COLORS = {
  Action: "#e05252", Comedy: "#e0a952", Drama: "#52a0e0",
  Horror: "#9952e0", Romance: "#e05296", "Sci-Fi": "#52e0c8",
  Thriller: "#c8e052", Animation: "#52e07c", Documentary: "#e08052",
};

function StarRating({ rating }) {
  const full  = Math.floor(rating);
  const half  = rating % 1 >= 0.5;
  return (
    <span style={{ color: "var(--accent)", letterSpacing: 1, fontSize: 13 }}>
      {"★".repeat(full)}
      {half ? "½" : ""}
      {"☆".repeat(5 - full - (half ? 1 : 0))}
      <span style={{ color: "var(--muted)", marginLeft: 6, fontSize: 12 }}>
        {rating.toFixed(1)}
      </span>
    </span>
  );
}

export function ItemCard({ item, type, index }) {
  const [expanded, setExpanded] = useState(false);
  const isMovie = type === "movie";

  const genres = isMovie
    ? (item.genres || "").split(" ").filter(Boolean).slice(0, 3)
    : [];

  return (
    <div
      className="fade-up"
      style={{
        animationDelay: `${index * 80}ms`,
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: 12,
        cursor: "default",
        transition: "border-color 0.2s, transform 0.2s",
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = "rgba(200,169,110,0.3)";
        e.currentTarget.style.transform = "translateY(-2px)";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = "var(--border)";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
        {/* Type icon */}
        <div style={{
          width: 44, height: 44, borderRadius: 10, flexShrink: 0,
          background: isMovie ? "rgba(124,106,240,0.15)" : "rgba(200,169,110,0.12)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 22, border: `1px solid ${isMovie ? "rgba(124,106,240,0.2)" : "rgba(200,169,110,0.2)"}`,
        }}>
          {isMovie ? "🎬" : "📖"}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{
            fontFamily: "var(--font-disp)",
            fontSize: "1rem",
            lineHeight: 1.3,
            marginBottom: 2,
            color: "var(--text)",
          }}>
            {item.title}
          </h3>
          <div style={{ fontSize: 12, color: "var(--muted)" }}>
            {isMovie
              ? `${item.year || "—"} · ${(item.rating_count || 0).toLocaleString()} ratings`
              : `${item.author || "Unknown"} · ${(item.rating_count || 0).toLocaleString()} ratings`
            }
          </div>
        </div>
      </div>

      {/* Rating */}
      {item.avg_rating > 0 && <StarRating rating={item.avg_rating} />}

      {/* Genre tags (movies) */}
      {genres.length > 0 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {genres.map(g => (
            <span key={g} style={{
              fontSize: 11, padding: "2px 8px",
              background: `${GENRE_COLORS[g] || "#52a0e0"}18`,
              color: GENRE_COLORS[g] || "#52a0e0",
              border: `1px solid ${GENRE_COLORS[g] || "#52a0e0"}33`,
              borderRadius: 20,
            }}>
              {g}
            </span>
          ))}
        </div>
      )}

      {/* Score bars */}
      <div>
        <ScoreBar label="Content match"   value={item.content_score} color="var(--accent2)" />
        <ScoreBar label="Collab / Pop."   value={item.collab_score}  color="var(--green)"   />
        <ScoreBar label="Hybrid score"    value={item.hybrid_score}  color="var(--accent)"  />
      </div>

      {/* Expand toggle */}
      <button
        onClick={() => setExpanded(v => !v)}
        style={{
          background: "none", border: "none", color: "var(--muted)",
          fontSize: 12, cursor: "pointer", textAlign: "left", padding: 0,
        }}
      >
        {expanded ? "▲ less" : "▼ score breakdown"}
      </button>

      {expanded && (
        <div style={{
          fontSize: 12, color: "var(--muted)",
          background: "rgba(255,255,255,0.03)",
          borderRadius: 8, padding: "10px 12px",
          lineHeight: 1.8,
        }}>
          <div>Content score &nbsp;<b style={{color:"var(--accent2)"}}>{(item.content_score*100).toFixed(1)}%</b> — how well this item's text matches your query via TF-IDF cosine similarity.</div>
          <div>Collab / pop. &nbsp;<b style={{color:"var(--green)"}}>{(item.collab_score*100).toFixed(1)}%</b> — user-based SVD predicted rating (or popularity if no user ID).</div>
          <div>Hybrid &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style={{color:"var(--accent)"}}>{(item.hybrid_score*100).toFixed(1)}%</b> — 60% content + 40% collaborative.</div>
        </div>
      )}
    </div>
  );
}
