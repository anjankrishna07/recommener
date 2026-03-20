import { useRecommend } from "./hooks/useRecommend";
import { SearchBar } from "./components/SearchBar";
import { ResultsGrid } from "./components/ResultsGrid";

function Hero() {
  return (
    <div style={{ textAlign: "center", marginBottom: 52 }}>
      {/* Decorative line */}
      <div style={{
        width: 1, height: 60, background: "linear-gradient(to bottom, transparent, var(--accent))",
        margin: "0 auto 32px",
      }} />

      <div style={{
        display: "inline-block",
        fontSize: 11, letterSpacing: 3, color: "var(--accent)",
        textTransform: "uppercase", marginBottom: 16,
        fontWeight: 500,
      }}>
        Hybrid ML Recommender
      </div>

      <h1 style={{
        fontFamily: "var(--font-disp)",
        fontSize: "clamp(2.2rem, 6vw, 3.8rem)",
        lineHeight: 1.1,
        marginBottom: 20,
        background: "linear-gradient(135deg, #e8e6f0 30%, #c8a96e)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        backgroundClip: "text",
      }}>
        What are you in
        <br />
        <em>the mood for?</em>
      </h1>

      <p style={{
        color: "var(--muted)",
        maxWidth: 480,
        margin: "0 auto 40px",
        fontSize: "1rem",
        lineHeight: 1.7,
      }}>
        Describe any interest, theme, or vibe. Our hybrid model combines
        TF-IDF content similarity with SVD collaborative filtering to find
        the perfect movies and books for you.
      </p>

      {/* ML pill badges */}
      <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap", marginBottom: 48 }}>
        {[
          { label: "TF-IDF", color: "var(--accent2)" },
          { label: "Cosine Similarity", color: "var(--accent2)" },
          { label: "SVD Matrix Factorization", color: "var(--green)" },
          { label: "Hybrid Blending", color: "var(--accent)" },
        ].map(({ label, color }) => (
          <span key={label} style={{
            fontSize: 11, padding: "4px 12px",
            background: `${color}12`,
            color, border: `1px solid ${color}30`,
            borderRadius: 20, fontWeight: 500,
          }}>
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 48 }}>
      {["Movies", "Books"].map(section => (
        <div key={section}>
          <div style={{
            width: 140, height: 24, borderRadius: 6, marginBottom: 20,
            background: "linear-gradient(90deg, #1a1a24 25%, #22222e 50%, #1a1a24 75%)",
            backgroundSize: "600px 100%",
            animation: "shimmer 1.5s infinite",
          }} />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} style={{
                height: 220, borderRadius: "var(--radius)",
                background: "linear-gradient(90deg, #13131a 25%, #1c1c27 50%, #13131a 75%)",
                backgroundSize: "600px 100%",
                animation: `shimmer 1.5s ${i * 0.15}s infinite`,
              }} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const { data, loading, error, recommend } = useRecommend();

  return (
    <div style={{
      minHeight: "100vh",
      background: `
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(124,106,240,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 90%, rgba(200,169,110,0.05) 0%, transparent 60%),
        var(--bg)
      `,
    }}>
      <div style={{
        maxWidth: 1100,
        margin: "0 auto",
        padding: "clamp(40px, 8vw, 80px) 24px 80px",
      }}>
        <Hero />
        <SearchBar onSearch={recommend} loading={loading} />

        <div style={{ marginTop: 64 }}>
          {loading && <SkeletonGrid />}
          {error && (
            <div style={{
              padding: "20px 24px",
              background: "rgba(224,82,82,0.08)",
              border: "1px solid rgba(224,82,82,0.2)",
              borderRadius: 10, color: "#e05252",
              fontSize: 14,
            }}>
              <strong>Error:</strong> {error}
              {error.includes("Model not found") && (
                <div style={{ marginTop: 8, color: "var(--muted)", fontSize: 13 }}>
                  Run <code style={{ background: "rgba(255,255,255,0.08)", padding: "2px 6px", borderRadius: 4 }}>
                    python scripts/prepare_data.py && python scripts/train.py
                  </code> first.
                </div>
              )}
            </div>
          )}
          {data && !loading && <ResultsGrid data={data} />}

          {!data && !loading && !error && (
            <div style={{
              textAlign: "center", color: "var(--muted)",
              marginTop: 40, fontSize: 14,
            }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>✦</div>
              Enter any interest above to get personalised recommendations
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
