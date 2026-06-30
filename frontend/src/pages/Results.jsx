import { useLocation, useNavigate } from "react-router-dom";
import ScoreRing from "../components/ScoreRing.jsx";
import KeywordBadge from "../components/KeywordBadge.jsx";

const styles = {
  page: {
    minHeight:     "100vh",
    background:    "var(--bg)",
    display:       "flex",
    flexDirection: "column",
  },
  header: {
    borderBottom: "1px solid var(--border)",
    padding:      "20px 40px",
    display:      "flex",
    alignItems:   "center",
    justifyContent:"space-between",
  },
  logo: {
    fontFamily: "var(--font-serif)",
    fontSize:   "1.4rem",
    color:      "var(--text)",
  },
  logoAccent: {
    color: "var(--accent)",
  },
  backBtn: {
    background:   "none",
    border:       "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding:      "7px 16px",
    fontSize:     "0.85rem",
    fontWeight:   500,
    color:        "var(--text)",
    cursor:       "pointer",
    fontFamily:   "var(--font-sans)",
    transition:   "border-color 0.2s",
  },
  main: {
    maxWidth: "860px",
    margin:   "0 auto",
    padding:  "48px 24px 80px",
    width:    "100%",
  },
  topRow: {
    display:       "flex",
    alignItems:    "flex-start",
    gap:           "40px",
    marginBottom:  "40px",
    flexWrap:      "wrap",
  },
  scoreCol: {
    display:       "flex",
    flexDirection: "column",
    alignItems:    "center",
    gap:           "8px",
    flexShrink:    0,
  },
  metaCol: {
    flex: 1,
    minWidth: "240px",
  },
  targetRole: {
    fontFamily:   "var(--font-serif)",
    fontSize:     "clamp(1.4rem, 4vw, 2rem)",
    color:        "var(--text)",
    lineHeight:   1.2,
    marginBottom: "8px",
  },
  roleLabel: {
    fontSize:      "0.75rem",
    fontWeight:    600,
    color:         "var(--muted)",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    marginBottom:  "6px",
  },
  section: {
    marginBottom: "32px",
  },
  sectionTitle: {
    fontFamily:    "var(--font-serif)",
    fontSize:      "1.1rem",
    color:         "var(--text)",
    marginBottom:  "14px",
    paddingBottom: "8px",
    borderBottom:  "1px solid var(--border)",
  },
  card: {
    background:   "var(--surface)",
    border:       "1px solid var(--border)",
    borderRadius: "var(--radius)",
    padding:      "20px 24px",
    marginBottom: "12px",
  },
  cardLabel: {
    fontSize:      "0.72rem",
    fontWeight:    600,
    color:         "var(--muted)",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    marginBottom:  "4px",
  },
  cardText: {
    fontSize:   "0.9rem",
    color:      "var(--text)",
    lineHeight: 1.6,
  },
  badgeRow: {
    display:   "flex",
    flexWrap:  "wrap",
    gap:       "8px",
    marginTop: "4px",
  },
  suggestionItem: {
    display:      "flex",
    gap:          "12px",
    padding:      "14px 16px",
    background:   "var(--surface)",
    border:       "1px solid var(--border)",
    borderRadius: "var(--radius)",
    marginBottom: "10px",
    fontSize:     "0.9rem",
    color:        "var(--text)",
    lineHeight:   1.6,
  },
  suggestionNum: {
    flexShrink:  0,
    width:       "22px",
    height:      "22px",
    borderRadius:"50%",
    background:  "var(--accent-lt)",
    color:       "var(--accent)",
    fontSize:    "0.75rem",
    fontWeight:  700,
    display:     "flex",
    alignItems:  "center",
    justifyContent:"center",
    marginTop:   "1px",
  },
  flagItem: {
    display:      "flex",
    alignItems:   "center",
    gap:          "8px",
    padding:      "10px 14px",
    background:   "var(--red-lt)",
    border:       "1px solid #fecaca",
    borderRadius: "var(--radius)",
    marginBottom: "8px",
    fontSize:     "0.875rem",
    color:        "var(--red)",
  },
  emptyState: {
    fontSize:  "0.875rem",
    color:     "var(--muted)",
    fontStyle: "italic",
  },
  feedbackGrid: {
    display:             "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
    gap:                 "12px",
  },
};

export default function Results() {
  const { state }  = useLocation();
  const navigate   = useNavigate();
  const result     = state?.result;
  const hasJD      = !!state?.jobDescription?.trim();

  if (!result) {
    return (
      <div style={{ padding: "60px 24px", textAlign: "center" }}>
        <p style={{ color: "var(--muted)", marginBottom: "16px" }}>No results found.</p>
        <button style={styles.backBtn} onClick={() => navigate("/")}>
          ← Back to checker
        </button>
      </div>
    );
  }

  const {
    target_role       = "",
    ats_score         = 0,
    matched_keywords  = [],
    missing_keywords  = [],
    suggested_keywords= [],
    section_feedback  = {},
    bullet_quality    = "",
    formatting_flags  = [],
    suggestions       = [],
  } = result;

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={{ ...styles.header, justifyContent: "center", borderBottom: "none", paddingBottom: 0, position: "relative" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <img src="/logo.svg" alt="pauseresume.ai logo" style={{ height: "48px", width: "auto" }} />
          <div style={{ ...styles.logo, fontSize: "clamp(2.2rem, 6vw, 3.2rem)" }}>
            pause<span style={styles.logoAccent}>resume</span>.ai
          </div>
        </div>
        <button style={{ ...styles.backBtn, position: "absolute", right: "24px", top: "50%" , transform: "translateY(-50%)" }} onClick={() => navigate("/")}>
          ← Check another
        </button>
      </header>

      <main style={styles.main}>

        {/* Top row — score + role */}
        <div style={styles.topRow}>
          <div style={styles.scoreCol}>
            <ScoreRing score={ats_score} size={160} />
          </div>
          <div style={styles.metaCol}>
            <div style={styles.roleLabel}>Target Role</div>
            <div style={styles.targetRole}>
              {target_role || "Not detected"}
            </div>
            <div style={{ fontSize: "0.85rem", color: "var(--muted)", lineHeight: 1.6 }}>
              {hasJD
                ? "Analysed against the job description you provided."
                : "No job description provided — general ATS quality analysis."}
            </div>
          </div>
        </div>

        {/* Keywords — only show if JD was provided */}
        {hasJD && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Keyword Analysis</div>

            {matched_keywords.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <div style={styles.cardLabel}>Matched ({matched_keywords.length})</div>
                <div style={styles.badgeRow}>
                  {matched_keywords.map((w) => (
                    <KeywordBadge key={w} word={w} variant="matched" />
                  ))}
                </div>
              </div>
            )}

            {missing_keywords.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <div style={styles.cardLabel}>Missing ({missing_keywords.length})</div>
                <div style={styles.badgeRow}>
                  {missing_keywords.map((w) => (
                    <KeywordBadge key={w} word={w} variant="missing" />
                  ))}
                </div>
              </div>
            )}

            {suggested_keywords.length > 0 && (
              <div>
                <div style={styles.cardLabel}>Suggested to add ({suggested_keywords.length})</div>
                <div style={styles.badgeRow}>
                  {suggested_keywords.map((w) => (
                    <KeywordBadge key={w} word={w} variant="suggested" />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Suggested keywords in general mode */}
        {!hasJD && suggested_keywords.length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Skills to Consider Adding</div>
            <div style={styles.badgeRow}>
              {suggested_keywords.map((w) => (
                <KeywordBadge key={w} word={w} variant="suggested" />
              ))}
            </div>
          </div>
        )}

        {/* Section feedback */}
        {Object.keys(section_feedback).length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Section Feedback</div>
            <div style={styles.feedbackGrid}>
              {Object.entries(section_feedback).map(([sec, feedback]) => (
                feedback ? (
                  <div key={sec} style={styles.card}>
                    <div style={styles.cardLabel}>{sec}</div>
                    <div style={styles.cardText}>{feedback}</div>
                  </div>
                ) : null
              ))}
            </div>
          </div>
        )}

        {/* Bullet quality */}
        {bullet_quality && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Bullet Quality</div>
            <div style={styles.card}>
              <div style={styles.cardText}>{bullet_quality}</div>
            </div>
          </div>
        )}

        {/* Formatting flags */}
        <div style={styles.section}>
          <div style={styles.sectionTitle}>Formatting Flags</div>
          {formatting_flags.length > 0 ? (
            formatting_flags.map((flag, i) => (
              <div key={i} style={styles.flagItem}>
                <span>⚠</span> {flag}
              </div>
            ))
          ) : (
            <div style={styles.emptyState}>No formatting issues detected.</div>
          )}
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Recommendations</div>
            {suggestions.map((s, i) => (
              <div key={i} style={styles.suggestionItem}>
                <div style={styles.suggestionNum}>{i + 1}</div>
                <div>{s}</div>
              </div>
            ))}
          </div>
        )}

      </main>
    </div>
  );
}