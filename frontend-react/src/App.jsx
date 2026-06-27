import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: true,
  theme: "dark",
  securityLevel: "loose",
  fontFamily: "ui-sans-serif, system-ui",
});

const Mermaid = ({ chart }) => {
  const ref = useRef(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (ref.current && chart) {
      setError(false);
      mermaid.render(`mermaid-${Math.random().toString(36).substr(2, 9)}`, chart)
        .then(({ svg }) => {
          if (ref.current) {
            ref.current.innerHTML = svg;
            setError(false);
          }
        })
        .catch(() => {
          if (ref.current) ref.current.innerHTML = "";
          setError(true);
        });
    }
  }, [chart]);

  return (
    <div className="mermaid-outer">
      <div ref={ref} className="mermaid-container" />
      {error && (
        <div className="mermaid-container">
          <div className="mermaid-error">
            Diagram could not be rendered — the AI-generated syntax may be invalid. Raw diagram data is available in the report text.
          </div>
        </div>
      )}
    </div>
  );
};

const API_BASE = "http://localhost:8000";

function fmtTime(ts) {
  try {
    return new Date(ts * 1000).toLocaleString();
  } catch {
    return String(ts);
  }
}

function downloadTextFile(filename, text) {
  const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function apiJson(path, { method = "GET", body, token } = {}) {
  const headers = {};
  if (body) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

function PhaseLoader({ active, phaseIndex, isComplete }) {
  const phases = useMemo(
    () => [
      { id: "req", name: "Requirement Analysis", icon: "📋" },
      { id: "val", name: "Structural Validation", icon: "🛡️" },
      { id: "plan", name: "Strategic Planning", icon: "📐" },
      { id: "risk", name: "Risk Mitigation", icon: "⚠️" },
      { id: "exec", name: "Executive Synthesis", icon: "⏳" },
    ],
    []
  );
  if (!active && !isComplete) return null;

  return (
    <div className="card loading-card" style={{ marginBottom: 24 }}>
      <div className="cardInner">
        <div className="fieldLabel">
          <span>{isComplete ? "Audit Complete" : "Project Audit Pipeline"}</span>
          <span className="hint">{isComplete ? "Review your report below" : "Autonomous Review Board"}</span>
        </div>
        <div className="phase-container">
          {phases.map((p, idx) => {
            const state =
              idx < phaseIndex || isComplete ? "Verified" : idx === phaseIndex ? "Analyzing…" : "Pending";
            const stateClass =
              idx < phaseIndex || isComplete ? "phaseDone" : idx === phaseIndex ? "phaseActive" : "";
            
            return (
              <div className={`phaseRow ${idx === phaseIndex && !isComplete ? 'pulse-row' : ''}`} key={p.id}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div className="phaseIcon">
                    {idx < phaseIndex || isComplete ? '✅' : idx === phaseIndex ? <div className="phase-spinner" /> : p.icon}
                  </div>
                  <div className="phaseName">{p.name}</div>
                </div>
                <div className={`phaseState ${stateClass}`}>{state}</div>
              </div>
            );
          })}
        </div>
        {!isComplete && (
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${(phaseIndex / 5) * 100}%` }} />
            <div className="progress-label">Step {phaseIndex + 1} of 5</div>
          </div>
        )}
      </div>
    </div>
  );
}

function ErrorDisplay({ error, onRetry, onSwitch, onClose }) {
  if (!error) return null;

  const isRateLimit = error.includes("429") || error.includes("limit");
  
  const content = (
    <div className="card error-card" style={{ marginBottom: 0, paddingRight: 40 }}>
      <button 
        className="error-toast-close" 
        onClick={onClose}
        aria-label="Close error"
      >
        ×
      </button>
      <div className="cardInner">
        <div className="error-header">
          <div className="error-icon">⚠️</div>
          <div className="error-title">
            {isRateLimit ? "AI Provider Limit Reached" : "Audit Execution Fault"}
          </div>
        </div>
        <div className="error-body">
          <p>
            {isRateLimit 
              ? "The primary intelligence provider has reached its daily quota. This usually resolves within a few minutes."
              : "An unexpected error occurred during the multi-agent orchestration. Please check your project specification."}
          </p>
          
          <div className="error-actions btnRow">
            <button className="btn btnPrimary" onClick={onRetry}>Retry Analysis</button>
            {isRateLimit && <button className="btn" onClick={onSwitch}>Switch to Fallback (Gemini)</button>}
          </div>

          <details className="error-details">
            <summary>Technical Diagnostics</summary>
            <pre>{error}</pre>
          </details>
        </div>
      </div>
    </div>
  );

  return (
    <div className="error-inline">
      {content}
    </div>
  );
}

function ReportDashboard({ reportMd, projectName }) {
  const readiness = useMemo(() => {
    const match = reportMd.match(/Overall Readiness:\s*(\d+)%/i);
    return match ? match[1] : "0";
  }, [reportMd]);

  const decision = useMemo(() => {
    // Gracefully extracts the decision keyword regardless of surrounding
    // bold tags (**), colons, dashes, or plain whitespace. Longest
    // alternatives are listed first so "GO WITH CONDITIONS" is captured
    // in full rather than short-circuiting on "GO".
    const match = reportMd.match(
      /Decision\s*[:\-]?\s*\*{0,2}\s*(GO WITH CONDITIONS|GO WITH|GO|BLOCKED)\s*\*{0,2}/i
    );
    // NOTE: defaults to "UNKNOWN" (not "BLOCKED") when no decision field
    // is found at all. Defaulting to BLOCKED on a missing/unparseable
    // field would silently tell a CTO the project is blocked when the
    // real status is simply unknown — that's a misleading risk signal,
    // not a safe fallback.
    return match ? match[1].toUpperCase().trim() : "UNKNOWN";
  }, [reportMd]);

  const scores = useMemo(() => {
    // Flexible, case-insensitive engine that tolerates either the legacy
    // Markdown table pipe layout ("Architecture | 2") OR free-form inline
    // agent text ("Architecture: 2/10 (due to monolithic design...)").
    //
    // Strategy: find the keyword, then look at whatever immediately
    // follows it (allowing for ":", "|", "**", brackets, etc.) and pull
    // out the first standalone number in that trailing chunk. A number
    // is treated as a /10 score (and scaled x10) unless it's already
    // followed by a "%", in which case it's used as-is.
    const keywords = {
      Architecture: "Architecture",
      Security: "Security",
      Compliance: "Compliance",
      "Req. Quality": "Requirements Quality",
    };

    const extractScore = (md, keyword) => {
      // Escape the keyword in case it ever contains regex-special chars.
      const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

      // Capture a window of text after the keyword: optional separators
      // (colon, pipe, asterisks, dashes, whitespace) followed by the
      // first number, then optionally a "%" or "/10" style suffix.
      const re = new RegExp(
        `\\**${escaped}\\**\\s*(?:Score|Rating)?\\**\\s*[:|\\-\\s]*\\**\\s*\\(?\\s*\\**(\\d{1,3}(?:\\.\\d+)?)\\**\\s*(%|\\s*\\/\\s*10)?`,
        "i"
      );

      const m = md.match(re);
      if (!m) return null;

      const rawNum = parseFloat(m[1]);
      const isPercent = m[2] && m[2].trim().startsWith("%");

      if (Number.isNaN(rawNum)) return null;

      let normalized;
      if (isPercent) {
        // Already a percentage (e.g. "Architecture: 82%")
        normalized = Math.round(rawNum);
      } else if (rawNum >= 1 && rawNum <= 10) {
        // Standard 10-point scale -> normalize to 100% scale
        normalized = Math.round(rawNum * 10);
      } else {
        // Fallback: clamp anything else into a sane 0-100 range
        normalized = Math.round(Math.min(Math.max(rawNum, 0), 100));
      }

      return normalized;
    };

    return Object.entries(keywords).map(([label, keyword]) => {
      const score = extractScore(reportMd, keyword);
      return { label, value: score !== null ? `${score}%` : "N/A" };
    });
  }, [reportMd]);

  const metrics = useMemo(() => {
    const extractors = {
      "Risk Level": (md) => {
        const m = md.match(/Risk Level[:\s*\[]*\**\s*(Critical|High|Medium|Low)\b/i);
        return m ? m[1] : "N/A";
      },
      "Timeline": (md) => {
        const m = md.match(/(?:Estimated\s+)?Timeline[:\s*\[]*\**\s*([\d]+\s+weeks?|N\/A)\b/i);
        return m ? m[1] : "N/A";
      },
      "Complexity": (md) => {
        const m = md.match(/Complexity[:\s*\[]*\**\s*(Critical|High|Medium|Low)\b/i);
        return m ? m[1] : "N/A";
      },
    };
    return Object.entries(extractors).map(([label, fn]) => ({
      label,
      value: fn(reportMd),
    }));
  }, [reportMd]);

  const executiveSummary = useMemo(() => {
    const match = reportMd.match(/## 2\. EXECUTIVE SUMMARY\n([\s\S]*?)(?=\n##|$)/i);
    return match ? match[1].trim() : "Analysis complete. Access detailed logs below.";
  }, [reportMd]);

  const blueprint = useMemo(() => {
    const match = reportMd.match(/```mermaid\n([\s\S]*?)\n```/i);
    return match ? match[1].trim() : null;
  }, [reportMd]);

  const badgeClass = useMemo(() => {
    if (decision.includes("GO WITH")) return "badge-condition";
    if (decision.includes("GO")) return "badge-go";
    if (decision.includes("BLOCKED")) return "badge-blocked";
    return "";
  }, [decision]);

  return (
    <div className="dashboard-root">
      <header className="dashHeader">
        <div className="dashTitle">
          <p className="overline">CTO ADVISORY • {new Date().toLocaleDateString()}</p>
          <h1>{projectName}</h1>
        </div>
        <div className={`badge large-badge ${badgeClass}`}>
          {decision}
        </div>
      </header>

      <div className="scoreGrid">
        <div className="scoreCard hero-card">
          <div className="scoreLabel">Overall Readiness</div>
          <div className="readinessLarge">{readiness}%</div>
          <div className="scoreDesc">Consolidated Enterprise Confidence Score</div>
        </div>
        
        <div className="mini-scores">
          {scores.map((s) => (
            <div key={s.label} className="scoreCard mini">
              <div className="scoreLabel">{s.label}</div>
              <div className="scoreValue">{s.value}</div>
            </div>
          ))}
        </div>

        <div className="metric-scores">
          {metrics.map((s) => (
            <div key={s.label} className="scoreCard metric">
              <div className="scoreLabel">{s.label}</div>
              <div className="scoreValue">{s.value}</div>
            </div>
          ))}
        </div>
      </div>

      {blueprint && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="cardInner">
            <div className="fieldLabel">System Architectural Blueprint</div>
            <div className="mermaid-container" style={{ background: 'rgba(0,0,0,0.1)', border: 'none', padding: 0 }}>
              <Mermaid chart={blueprint} />
            </div>
          </div>
        </div>
      )}

      <div className="card summary-card" style={{ marginBottom: 32 }}>
        <div className="cardInner">
          <div className="fieldLabel">Executive Synthesis</div>
          <div className="md summary-text">
            {executiveSummary}
          </div>
        </div>
      </div>
    </div>
  );
}

// Find this component inside your App.jsx and replace it with this fixed version:
// frontend-react/src/App.jsx (Updated ReportViewer & Cleaned Layout Extractors)

// Shared ReactMarkdown `code` override used by both the main report body
// and the collapsible traceability/appendix body.
//
// Rules:
//   1. Only ever mount <Mermaid /> when the className explicitly carries
//      the "language-mermaid" token AND the block is a fenced block
//      (not an inline `code` span).
//   2. Even if "language-mermaid" is present, bail out to plain
//      pre-formatted text if the raw content looks like a structural
//      worklog/log line (contains whole-word PHASE, STATUS, or
//      requirements) rather than real Mermaid diagram syntax. Raw agent
//      logs sometimes get fenced with a stray "mermaid" tag by the LLM,
//      or just happen to contain those words — we don't want to hand
//      that text to the Mermaid compiler and get a vector-canvas syntax
//      explosion in the appendix.
//   3. Anything that falls through renders as a normal dark-glass
//      monospaced block, matching the surrounding report aesthetic.
const WORKLOG_EXCLUSION_RE = /\b(PHASE|STATUS|requirements)\b/i;

function MarkdownCodeBlock({ inline, className, children, ...props }) {
  const raw = String(children ?? "").replace(/\n$/, "");
  const isMermaidTagged = /language-mermaid/.test(className || "");
  const looksLikeWorklog = WORKLOG_EXCLUSION_RE.test(raw);

  const shouldRenderMermaid = !inline && isMermaidTagged && !looksLikeWorklog;

  if (shouldRenderMermaid) {
    return <Mermaid chart={raw} />;
  }

  if (!inline) {
    // Block-level, but not a genuine Mermaid diagram (either untagged,
    // or tagged-but-actually-a-worklog). Render as a dark-glass
    // pre-formatted monospace block instead of risking the Mermaid
    // compiler on plain text.
    return (
      <pre
        className="worklog-pre"
        style={{
          background: "rgba(10, 14, 22, 0.55)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          borderRadius: "10px",
          padding: "16px 18px",
          overflowX: "auto",
          backdropFilter: "blur(6px)",
          WebkitBackdropFilter: "blur(6px)",
          margin: "12px 0",
        }}
      >
        <code
          className="worklog-code"
          style={{
            fontFamily:
              "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace",
            fontSize: "13px",
            lineHeight: 1.6,
            color: "rgba(226, 232, 240, 0.92)",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
          {...props}
        >
          {raw}
        </code>
      </pre>
    );
  }

  // Inline code spans render normally.
  return (
    <code className={className} {...props}>
      {children}
    </code>
  );
}

function ReportViewer({ reportMd, exportFilename }) {
  const [activeId, setActiveId] = useState("");
  const [expandedSections, setExpandedSections] = useState({ traceability: false, appendix: false });
  
  // FIXED: Repaired heading token selector string matching algorithm to prevent single-letter truncation
  const sections = useMemo(() => {
    const matches = Array.from(reportMd.matchAll(/^(##|###)\s+(.*)$/gm));
    const processed = new Set();
    
    return matches.map(m => {
      const title = m[2].trim();
      const id = title.toLowerCase().replace(/[^\w]+/g, '-');
      if (processed.has(id)) return null;
      processed.add(id);
      return {
        title,
        id,
        level: m[1].length
      };
    }).filter(s => s && (s.level === 2 || s.level === 3));
  }, [reportMd]);

  // Intersection observer tracking scroll-spy logic
  useEffect(() => {
    const observer = new IntersectionObserver( entries => {
      const visible = entries.find(e => e.isIntersecting);
      if (visible) setActiveId(visible.target.id);
    }, { rootMargin: '-20% 0px -70% 0px' });

    document.querySelectorAll('.md h2, .md h3').forEach(el => {
      const id = el.textContent.toLowerCase().replace(/[^\w]+/g, '-');
      el.id = id;
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, [reportMd]);

  const parts = useMemo(() => {
    const splitIndex = reportMd.search(/## 7\. REQUIREMENT TRACEABILITY/i);
    if (splitIndex === -1) return { main: reportMd, details: "" };
    return {
      main: reportMd.slice(0, splitIndex),
      details: reportMd.slice(splitIndex)
    };
  }, [reportMd]);

  return (
    <div className="report-layout">
      <nav
        className="toc-nav"
        style={{ minWidth: "280px", maxWidth: "280px", overflowX: "hidden" }}
      >
        <div className="toc-label">Document Sections</div>
        <div className="toc-links">
          {sections.map((s, idx) => (
            <a 
              key={`${s.id}-${s.level}-${idx}`} 
              href={`#${s.id}`} 
              className={`toc-link lvl-${s.level} ${activeId === s.id ? 'active' : ''}`}
            >
              {s.title}
            </a>
          ))}
        </div>
        <div style={{ marginTop: 'auto', paddingTop: 20, width: '100%' }}>
          <button className="btn btn-sm" onClick={() => window.print()} style={{ width: '100%', opacity: 0.7 }}>
            Print PDF / Archive
          </button>
        </div>
      </nav>

      <div className="report-content card">
        <div className="cardInner">
          <div className="md">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                code: MarkdownCodeBlock,
                h2: ({children, ...props}) => {
                  const txt = children?.toString() || "";
                  return <h2 id={txt.toLowerCase().replace(/[^\w]+/g, '-')} {...props}>{children}</h2>;
                },
                h3: ({children, ...props}) => {
                  const txt = children?.toString() || "";
                  return <h3 id={txt.toLowerCase().replace(/[^\w]+/g, '-')} {...props}>{children}</h3>;
                },
              }}
            >
              {parts.main}
            </ReactMarkdown>

            {parts.details && (
              <div className="collapsible-details">
                <button 
                  className="btn btn-ghost" 
                  onClick={() => setExpandedSections(p => ({...p, traceability: !p.traceability}))}
                  style={{ width: '100%', margin: '40px 0 20px', borderStyle: 'dashed' }}
                >
                  {expandedSections.traceability ? 'Collapse' : 'Show'} Detailed Requirement Traceability Matrix
                </button>
                {expandedSections.traceability && (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code: MarkdownCodeBlock,
                      h2: ({children, ...props}) => {
                        const txt = children?.toString() || "";
                        return <h2 id={txt.toLowerCase().replace(/[^\w]+/g, '-')} {...props}>{children}</h2>;
                      },
                      h3: ({children, ...props}) => {
                        const txt = children?.toString() || "";
                        return <h3 id={txt.toLowerCase().replace(/[^\w]+/g, '-')} {...props}>{children}</h3>;
                      },
                    }}
                  >
                    {parts.details}
                  </ReactMarkdown>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


export default function App() {
  const [mode, setMode] = useState("signin"); // signin | signup
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [authedUser, setAuthedUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);

  const [projectName, setProjectName] = useState("My Project");
  const [projectSpec, setProjectSpec] = useState("");

  const [history, setHistory] = useState([]);
  const [selectedAuditId, setSelectedAuditId] = useState(null);
  const [selectedAudit, setSelectedAudit] = useState(null);

  const [tab, setTab] = useState("report"); // report | raw
  const [status, setStatus] = useState("Disconnected");
  const [error, setError] = useState("");

  const [running, setRunning] = useState(false);
  const [phaseIndex, setPhaseIndex] = useState(0);
  const phaseTimerRef = useRef(null);

  const isSignedIn = !!authedUser;

  async function refreshHistory() {
    if (!accessToken) return;
    const data = await apiJson(`/audit/history?limit=50`, { token: accessToken });
    setHistory(data.items || []);
  }

  async function loadAudit(auditId) {
    if (!accessToken) return;
    const data = await apiJson(`/audit/${auditId}`, { token: accessToken });
    setSelectedAudit(data);
  }

  useEffect(() => {
    apiJson("/health")
      .then(() => setStatus("API Connected"))
      .catch(() => setStatus("API Offline"));
  }, []);

  useEffect(() => {
    if (!isSignedIn) return;
    refreshHistory().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSignedIn]);

  useEffect(() => {
    if (!selectedAuditId) return;
    loadAudit(selectedAuditId).catch((e) => setError(String(e.message || e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAuditId]);

  function startPhaseAnimation() {
    setPhaseIndex(0);
    if (phaseTimerRef.current) clearInterval(phaseTimerRef.current);
    phaseTimerRef.current = setInterval(() => {
      setPhaseIndex((i) => (i < 4 ? i + 1 : 4));
    }, 900);
  }

  function stopPhaseAnimation() {
    if (phaseTimerRef.current) clearInterval(phaseTimerRef.current);
    phaseTimerRef.current = null;
  }

  async function handleAuth() {
    setError("");
    try {
      const path = mode === "signup" ? "/auth/signup" : "/auth/signin";
      const data = await apiJson(path, {
        method: "POST",
        body: { username, password },
      });
      setAuthedUser({
        username: data.username,
        user_hash: data.user_hash,
        created_at: data.created_at,
      });
      setAccessToken(data.access_token);
      setStatus("Authenticated");
      await refreshHistory();
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  function handleSignOut() {
    setAuthedUser(null);
    setAccessToken(null);
    setHistory([]);
    setSelectedAuditId(null);
    setSelectedAudit(null);
    setStatus("Disconnected");
    setError("");
  }

  async function runAudit() {
    setError("");
    if (!projectSpec.trim() || projectSpec.trim().length < 10) {
      setError("Project spec is too short (min 10 chars).");
      return;
    }
    if (!accessToken) {
      setError("Authentication required. Please sign in.");
      return;
    }
    setRunning(true);
    startPhaseAnimation();
    // Refresh history to show audit is starting
    await refreshHistory().catch(() => {});
    try {
      const data = await apiJson("/audit/run", {
        method: "POST",
        body: {
          project_name: projectName,
          project_spec: projectSpec,
        },
        token: accessToken,
      });
      setError(""); // Clear any previous errors on success
      await refreshHistory();
      setSelectedAuditId(data.audit_id);
      setSelectedAudit({
        id: data.audit_id,
        project_name: data.project_name,
        report_md: data.report_md,
        model_used: data.model_used,
        created_at: data.created_at,
      });
      setTab("report");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      stopPhaseAnimation();
      setRunning(false);
    }
  }

  const reportMd = selectedAudit?.report_md || "";
  const exportFilename = useMemo(() => {
    const base = (selectedAudit?.project_name || projectName || "audit").replace(/[^\w\-]+/g, "_");
    const id = selectedAudit?.id ? `_${selectedAudit.id}` : "";
    return `SentinelIQ_Audit_${base}${id}.md`;
  }, [selectedAudit?.id, selectedAudit?.project_name, projectName]);

  return (
    <div className="appShell">
      <aside className="rail">
        <div className="brand">
          <div className="logoDot" />
          <div className="brandTitle">
            SentinelIQ
            <div className="brandSubtitle">Architecture Review Board</div>
          </div>
        </div>

        <div className="card">
          <div className="cardInner">
            <div className="topBar">
              <div className={`statusPill ${status === 'API Connected' || status === 'Authenticated' ? 'online' : 'offline'}`}>
                <span className="pulse" />
                <span>{status}</span>
              </div>
              {isSignedIn ? (
                <button className="btn btnDanger" onClick={handleSignOut}>
                  Sign out
                </button>
              ) : null}
            </div>

            {!isSignedIn ? (
              <>
                <div style={{ height: 10 }} />
                <div className="btnRow">
                  <button
                    className={`btn ${mode === "signin" ? "btnPrimary" : "btn-ghost"}`}
                    onClick={() => setMode("signin")}
                  >
                    Sign in
                  </button>
                  <button
                    className={`btn ${mode === "signup" ? "btnPrimary" : "btn-ghost"}`}
                    onClick={() => setMode("signup")}
                  >
                    Sign up
                  </button>
                </div>
                <div style={{ height: 12 }} />

                <div className="fieldLabel">
                  <span>Username</span>
                </div>
                <input
                  className="input"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <div style={{ height: 10 }} />
                <div className="fieldLabel">
                  <span>Password</span>
                  <span className="hint">min 8 chars</span>
                </div>
                <input
                  className="input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div style={{ height: 12 }} />
                <div className="btnRow">
                  <button className="btn btnPrimary" style={{ width: '100%' }} onClick={handleAuth}>
                    {mode === "signup" ? "Create account" : "Authenticate"}
                  </button>
                </div>
                <div style={{ height: 8 }} />
                <div className="hint">
                  Credentials are used only to scope your private audit history in SQLite.
                </div>
              </>
            ) : (
              <>
                <div style={{ height: 12 }} />
                <div className="fieldLabel">
                  <span>Signed in as</span>
                  <span className="hint">{authedUser.username}</span>
                </div>
                <div className="hint">
                  Audit history is isolated by your user hash and cannot be cross-read by other users.
                </div>
              </>
            )}
          </div>
        </div>

        <div className="card">
          <div className="cardInner">
            <div className="audit-archive-label">Audit Archive</div>
            <div className="audit-archive-divider"></div>
            <div className="fieldLabel">
              <button
                className="btn btn-sm"
                onClick={() => refreshHistory().catch((e) => setError(String(e.message || e)))}
              >
                Refresh
              </button>
            </div>
            <div className="historyList">
              {!isSignedIn ? (
                <div className="hint">Sign in to view your private audit archive.</div>
              ) : running ? (
                <div className="hint">⏳ Audit in progress...</div>
              ) : history.length === 0 ? (
                <div className="hint">No audits yet. Run your first audit from the main panel.</div>
              ) : (
                history.map((h) => {
                  const active = selectedAuditId === h.id;
                  return (
                    <div
                      key={h.id}
                      className={`historyItem ${active ? "historyItemActive" : ""}`}
                      onClick={() => setSelectedAuditId(h.id)}
                      title="Load audit"
                    >
                      <div className="historyMeta">
                        <span>#{h.id}</span>
                        <span>{fmtTime(h.created_at)}</span>
                      </div>
                      <div className="historyTitle">{h.project_name}</div>
                      <div className="historyMeta" style={{ marginTop: 6 }}>
                        <span>Model</span>
                        <span>{h.model_used}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <div className="mainGrid">
          <ErrorDisplay 
            error={error} 
            onRetry={runAudit} 
            onSwitch={() => { /* Logic to switch provider could go here if implemented */ }}
            onClose={() => setError("")}
          />

          {!selectedAudit && !running && (
            <div className="card hero-input-card">
              <div className="cardInner">
                <div className="dashTitle" style={{ marginBottom: 32 }}>
                  <p className="overline">System Ready</p>
                  <h1>Initiate New Architecture Audit</h1>
                </div>
                
                <div className="input-grid">
                  <div className="field-group">
                    <div className="fieldLabel">Project Identifier</div>
                    <input
                      className="input"
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                      placeholder="e.g. Project Phoenix"
                    />
                  </div>
                  <div className="field-group">
                    <div className="fieldLabel">Execution Profile</div>
                    <button
                      onClick={runAudit}
                      disabled={!isSignedIn || running}
                      data-action="run-audit"
                      className="btn btnPrimary hero-cta"
                      style={{ width: '100%' }}
                    >
                      {running ? "Analyzing Architecture…" : "Run Strategic Audit"}
                    </button>
                  </div>
                </div>

                <div style={{ height: 24 }} />
                <div className="fieldLabel">Detailed Project Scope / Specification</div>
                <textarea
                  className="input"
                  value={projectSpec}
                  onChange={(e) => setProjectSpec(e.target.value)}
                  rows={14}
                  placeholder="Paste your PRD, system requirements, or architectural spec here…"
                  style={{ resize: 'none' }}
                />
                <div className="hint-footer">
                  <span className="hint">Supports 10k+ character technical specs</span>
                  <span className="hint">5-Agent Review Panel active</span>
                </div>
              </div>
            </div>
          )}

          <PhaseLoader active={running} phaseIndex={phaseIndex} isComplete={!!selectedAudit && !running && tab !== 'raw'} />

          {selectedAudit && (
            <div className="report-container-fade-in">
              <ReportDashboard 
                reportMd={reportMd} 
                projectName={selectedAudit.project_name} 
              />

              <div style={{ height: 40 }} />
              
              <ReportViewer 
                reportMd={reportMd} 
                exportFilename={exportFilename} 
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}