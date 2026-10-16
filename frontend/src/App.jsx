
import { useCallback, useEffect, useState } from "react";
import {
  Activity, ArrowDownRight, ArrowRight, BookOpen, Check,
  CheckCircle2, ChevronDown, CircleAlert, Clock3, Database,
  FileQuestion, Gauge, LayoutDashboard, LoaderCircle, Plus,
  RefreshCw, ScanSearch, Search, Send, ShieldCheck, Sparkles,
  Tags, WandSparkles, XCircle
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail?.message || JSON.stringify(detail) || "Request failed";
    throw new Error(message);
  }
  return data;
}

function StatusBadge({ status }) {
  const value = (status || "unknown").toLowerCase();
  const accepted = value === "accepted" || value === "unique";
  const duplicate = value === "duplicate";

  return (
    <span className={`badge ${accepted ? "badge-green" : duplicate ? "badge-red" : "badge-amber"}`}>
      {accepted ? <CheckCircle2 size={13} /> : duplicate ? <XCircle size={13} /> : <CircleAlert size={13} />}
      {value.replaceAll("_", " ")}
    </span>
  );
}

function SectionTitle({ eyebrow, title, description, icon: Icon }) {
  return (
    <div className="section-heading">
      <div className="section-icon"><Icon size={20} /></div>
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("overview");
  const [questions, setQuestions] = useState([]);
  const [health, setHealth] = useState("checking");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [topic, setTopic] = useState("Reflection of light");
  const [count, setCount] = useState("5");
  const [tagsText, setTagsText] = useState('{"subject":"Physics","difficulty":"Beginner"}');
  const [generated, setGenerated] = useState([]);
  const [draft, setDraft] = useState("");
  const [checkResult, setCheckResult] = useState(null);
  const [search, setSearch] = useState("");
  const [newQuestion, setNewQuestion] = useState("");
  const [newTags, setNewTags] = useState('{"subject":"Physics"}');

  const refresh = useCallback(async () => {
    try {
      const [status, rows] = await Promise.all([
        fetch("http://127.0.0.1:8000/health").then(r => {
          if (!r.ok) throw new Error("API unavailable");
          return r.json();
        }),
        request("/questions?limit=500"),
      ]);
      setHealth(status.status === "ok" ? "online" : "offline");
      setQuestions(rows);
      setError("");
    } catch {
      setHealth("offline");
      setError("Cannot reach the backend. Start FastAPI on port 8000 and refresh.");
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  async function runAction(action) {
    setLoading(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (e) {
      setError(e.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function parseTags(text) {
    const value = JSON.parse(text || "{}");
    if (!value || Array.isArray(value) || typeof value !== "object") {
      throw new Error("Tags must be a JSON object, for example {\"subject\":\"Physics\"}.");
    }
    return value;
  }

  async function generate() {
    await runAction(async () => {
      const tags = parseTags(tagsText);
      const data = await request("/questions/generate", {
        method: "POST",
        body: JSON.stringify({ topic, count: Number(count), tags }),
      });
      setGenerated(data.results || []);
      setNotice(`${data.accepted_count} question(s) accepted and saved.`);
      await refresh();
    });
  }

  async function checkDuplicate() {
    await runAction(async () => {
      if (draft.trim().length < 5) throw new Error("Enter a question with at least 5 characters.");
      const data = await request("/duplicates/check", {
        method: "POST",
        body: JSON.stringify({ question: draft, tags: {} }),
      });
      setCheckResult(data);
    });
  }

  async function saveQuestion() {
    await runAction(async () => {
      const tags = parseTags(newTags);
      const data = await request("/questions", {
        method: "POST",
        body: JSON.stringify({ question: newQuestion, tags }),
      });
      setQuestions(old => [data, ...old]);
      setNewQuestion("");
      setNotice("Question saved successfully.");
    });
  }

  const filtered = questions.filter(q =>
    q.question.toLowerCase().includes(search.toLowerCase())
  );
  const accepted = generated.filter(q => q.status === "accepted").length;
  const duplicateCount = generated.filter(q => q.status === "duplicate").length;
  const reviewCount = generated.filter(q => q.status === "review").length;

  const nav = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "generate", label: "Generate questions", icon: WandSparkles },
    { id: "checker", label: "Duplicate checker", icon: ScanSearch },
    { id: "bank", label: "Question bank", icon: Database },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><LayersIcon /></div>
          <div>
            <strong>QuestionIQ</strong>
            <span>INTELLIGENCE PLATFORM</span>
          </div>
        </div>

        <div className="nav-caption">WORKSPACE</div>
        <nav>
          {nav.map(item => {
            const Icon = item.icon;
            return (
              <button key={item.id}
                className={`nav-link ${page === item.id ? "active" : ""}`}
                onClick={() => { setPage(item.id); setError(""); setNotice(""); }}>
                <Icon size={18} />
                <span>{item.label}</span>
                {page === item.id && <ArrowRight className="nav-arrow" size={15} />}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="system-card">
            <div className="system-card-top">
              <span className={`status-dot ${health === "online" ? "" : "dot-offline"}`} />
              <span>Backend status</span>
            </div>
            <strong>{health === "online" ? "Connected" : health === "checking" ? "Connecting..." : "Offline"}</strong>
            <span className="muted-small">FastAPI · localhost:8000</span>
            <button className="refresh-button" onClick={refresh}><RefreshCw size={13} /> Refresh status</button>
          </div>
          <div className="sidebar-footer"><ShieldCheck size={15} /> Independent duplicate validation</div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> <strong>{nav.find(n => n.id === page)?.label}</strong></div>
          <div className="topbar-right">
            <span className={`connection-pill ${health === "online" ? "connected" : ""}`}>
              <span className="status-dot" /> {health === "online" ? "System operational" : "API disconnected"}
            </span>
            <div className="avatar">QI</div>
          </div>
        </header>

        <div className="content">
          {error && <div className="alert alert-error"><CircleAlert size={18} /><span>{error}</span><button onClick={() => setError("")}><XCircle size={17}/></button></div>}
          {notice && <div className="alert alert-success"><CheckCircle2 size={18}/><span>{notice}</span><button onClick={() => setNotice("")}><XCircle size={17}/></button></div>}

          {page === "overview" && <>
            <div className="welcome-row">
              <div>
                <div className="eyebrow">YOUR WORKSPACE</div>
                <h1>Question intelligence, <span>simplified.</span></h1>
                <p>Generate better questions. Catch duplicates. Keep your knowledge base clean.</p>
              </div>
              <button className="button button-primary" onClick={() => setPage("generate")}><Sparkles size={16}/> Generate questions</button>
            </div>

            <div className="hero-panel">
              <div className="hero-copy">
                <div className="hero-label"><Sparkles size={14}/> AI-POWERED WORKFLOW</div>
                <h2>Quality questions start<br/>with smarter validation.</h2>
                <p>Generate educational questions with Gemini and independently check their meaning against your existing question bank.</p>
                <button className="button button-light" onClick={() => setPage("checker")}>Try duplicate checker <ArrowRight size={16}/></button>
              </div>
              <div className="hero-art">
                <div className="art-orbit orbit-one"></div>
                <div className="art-orbit orbit-two"></div>
                <div className="art-center"><FileQuestion size={42}/></div>
                <div className="art-float float-one"><CheckCircle2 size={17}/><span>Validated</span></div>
                <div className="art-float float-two"><ScanSearch size={18}/><span>Semantic match</span></div>
                <div className="art-float float-three"><Sparkles size={17}/><span>AI generated</span></div>
              </div>
            </div>

            <div className="metrics-grid">
              <Metric icon={Database} label="Saved questions" value={questions.length} caption="In your question bank" />
              <Metric icon={CheckCircle2} label="Accepted this session" value={accepted} caption="Passed duplicate detection" />
              <Metric icon={ScanSearch} label="Duplicates flagged" value={duplicateCount} caption="In latest generation" />
              <Metric icon={Clock3} label="Needs review" value={reviewCount} caption="In latest generation" />
            </div>

            <div className="section-grid">
              <section className="panel quick-panel">
                <div className="panel-heading"><div><h3>Quick actions</h3><p>Jump straight into your workflow</p></div><ArrowDownRight size={19}/></div>
                <button className="action-row" onClick={() => setPage("generate")}><div className="action-icon purple"><WandSparkles size={20}/></div><div><strong>Generate new questions</strong><span>Use AI to create original questions</span></div><ArrowRight size={17}/></button>
                <button className="action-row" onClick={() => setPage("checker")}><div className="action-icon blue"><ScanSearch size={20}/></div><div><strong>Check for duplicates</strong><span>Compare a question with existing content</span></div><ArrowRight size={17}/></button>
                <button className="action-row" onClick={() => setPage("bank")}><div className="action-icon green"><BookOpen size={20}/></div><div><strong>Explore question bank</strong><span>Search your saved questions</span></div><ArrowRight size={17}/></button>
              </section>

              <section className="panel recent-panel">
                <div className="panel-heading"><div><h3>Recently saved</h3><p>Latest questions in your repository</p></div><button className="text-button" onClick={() => setPage("bank")}>View all <ArrowRight size={14}/></button></div>
                {questions.length === 0 ? <Empty text="Your saved questions will appear here."/> :
                  questions.slice(0, 5).map((q, i) => <div className="recent-row" key={q.id || i}><div className="recent-number">{String(i+1).padStart(2,"0")}</div><div className="recent-question">{q.question}<span>{Object.entries(q.tags || {}).slice(0,2).map(([k,v]) => `${k}: ${v}`).join(" · ") || "No tags"}</span></div><CheckCircle2 className="recent-check" size={17}/></div>)}
              </section>
            </div>

            <div className="info-strip"><div className="info-icon"><Gauge size={19}/></div><div><strong>Built for responsible question generation</strong><p>Generation-time avoidance and independent duplicate detection are separate safeguards. Uncertain cases are surfaced for review.</p></div><button onClick={() => setPage("checker")}>Explore detection <ArrowRight size={15}/></button></div>
          </>}

          {page === "generate" && <>
            <SectionTitle eyebrow="AI WORKSPACE" title="Generate questions" description="Create new educational questions and validate each candidate before it enters your question bank." icon={WandSparkles}/>
            <div className="work-grid">
              <section className="panel form-panel">
                <div className="panel-heading"><div><h3>Generation settings</h3><p>Tell the AI what to create</p></div><Sparkles size={19}/></div>
                <label>Topic or subject</label>
                <input value={topic} onChange={e => setTopic(e.target.value)} placeholder="e.g. Machine learning fundamentals"/>
                <div className="form-two">
                  <div><label>Number of questions</label><select value={count} onChange={e => setCount(e.target.value)}>{[1,2,3,5,10,15,20].map(n => <option key={n} value={n}>{n} questions</option>)}</select></div>
                  <div><label>Generation model</label><div className="static-field"><Sparkles size={15}/> Gemini AI</div></div>
                </div>
                <label>Tags <span className="label-muted">JSON metadata</span></label>
                <textarea className="tag-input" rows={3} value={tagsText} onChange={e => setTagsText(e.target.value)} spellCheck="false"/>
                <div className="hint"><Tags size={14}/> Tags organize questions; they do not define duplicate identity.</div>
                <button className="button button-primary full-button" disabled={loading || health !== "online"} onClick={generate}>{loading ? <LoaderCircle className="spin" size={17}/> : <Sparkles size={17}/>} {loading ? "Generating and validating..." : "Generate & validate"} <ArrowRight size={16}/></button>
                {health !== "online" && <p className="form-footnote">Start your FastAPI backend to enable generation.</p>}
              </section>
              <section className="panel side-note">
                <div className="note-graphic"><ShieldCheck size={32}/></div>
                <h3>How validation works</h3>
                <div className="process-step"><span>01</span><div><strong>Context selection</strong><p>Relevant existing questions are provided to the LLM to reduce repetition.</p></div></div>
                <div className="process-step"><span>02</span><div><strong>Semantic comparison</strong><p>Sentence embeddings compare the candidate with saved questions.</p></div></div>
                <div className="process-step"><span>03</span><div><strong>Decision</strong><p>Unique questions are saved; duplicates and uncertain matches are flagged.</p></div></div>
              </section>
            </div>
            <section className="panel results-panel">
              <div className="panel-heading"><div><h3>Generation results</h3><p>{generated.length ? `${generated.length} candidates returned by the API` : "Your generated questions will appear here"}</p></div>{generated.length > 0 && <span className="results-count">{accepted} accepted</span>}</div>
              {generated.length === 0 ? <Empty text="Enter a topic and generate questions to see validation results."/> :
                generated.map((item,i) => <div className="result-row" key={`${item.question}-${i}`}><div className="result-index">{String(i+1).padStart(2,"0")}</div><div className="result-body"><strong>{item.question}</strong><p>{item.reason}</p></div><StatusBadge status={item.status}/></div>)}
            </section>
          </>}

          {page === "checker" && <>
            <SectionTitle eyebrow="VALIDATION LAB" title="Duplicate checker" description="Test a question against your existing bank using independent semantic detection." icon={ScanSearch}/>
            <div className="work-grid checker-grid">
              <section className="panel form-panel">
                <div className="panel-heading"><div><h3>Analyze a question</h3><p>Enter a question to check its similarity</p></div><Search size={19}/></div>
                <label>Question text</label>
                <textarea rows={5} value={draft} onChange={e => setDraft(e.target.value)} placeholder="e.g. Define the reflection of light."/>
                <div className="hint"><Activity size={14}/> The detector compares text and meaning, not tags.</div>
                <button className="button button-primary full-button" disabled={loading || health !== "online"} onClick={checkDuplicate}>{loading ? <LoaderCircle className="spin" size={17}/> : <ScanSearch size={17}/>} {loading ? "Analyzing..." : "Check for duplicates"} <ArrowRight size={16}/></button>
                <div className="sample-prompts"><span>Try an example</span><button onClick={() => setDraft("Define the reflection of light.")}>Semantic paraphrase</button><button onClick={() => setDraft("State the laws of reflection of light.")}>Different question</button></div>
              </section>
              <section className="panel checker-result">
                <div className="panel-heading"><div><h3>Detection result</h3><p>Analysis from your backend</p></div><ShieldCheck size={20}/></div>
                {!checkResult ? <div className="empty-result"><div><ScanSearch size={28}/></div><strong>Ready to analyze</strong><p>Submit a question to see its classification, similarity score, and closest matches.</p></div> :
                  <>
                    <div className="result-status"><span>Classification</span><StatusBadge status={checkResult.status}/></div>
                    <div className="score-block"><div><span>Best similarity</span><strong>{(Number(checkResult.best_similarity || 0)*100).toFixed(1)}<small>%</small></strong></div><div className="score-track"><div style={{width:`${Math.max(0,Math.min(100,Number(checkResult.best_similarity || 0)*100))}%`}}/></div></div>
                    <div className="explanation"><strong>Detector explanation</strong><p>{checkResult.explanation}</p></div>
                    <div className="matches-title">Closest matches <span>{checkResult.matches?.length || 0}</span></div>
                    {checkResult.matches?.length ? checkResult.matches.map((m,i) => <div className="match-row" key={`${m.question_id}-${i}`}><div><strong>{m.question}</strong><span>{m.match_type}</span></div><b>{(m.similarity*100).toFixed(1)}%</b></div>) : <p className="muted-copy">No close matches returned.</p>}
                  </>}
              </section>
            </div>
          </>}

          {page === "bank" && <>
            <SectionTitle eyebrow="KNOWLEDGE BASE" title="Question bank" description="Browse, search, and add questions to your local repository." icon={Database}/>
            <section className="panel bank-panel">
              <div className="bank-toolbar"><div><h3>Saved questions <span className="count-pill">{questions.length}</span></h3><p>Questions stored in the connected backend</p></div><button className="button button-primary" onClick={() => {setPage("add");}}><Plus size={16}/> Add question</button></div>
              <div className="search-box"><Search size={17}/><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search questions..."/>{search && <button onClick={() => setSearch("")}><XCircle size={16}/></button>}</div>
              {filtered.length === 0 ? <Empty text={questions.length ? "No questions match your search." : "Your question bank is empty. Generate or add a question to get started."}/> :
                <div className="table-wrap"><table><thead><tr><th>QUESTION</th><th>TAGS</th><th>CREATED</th><th>STATUS</th></tr></thead><tbody>{filtered.map((q,i) => <tr key={q.id || i}><td><div className="table-question"><span className="table-index">{String(i+1).padStart(2,"0")}</span>{q.question}</div></td><td><div className="tag-list">{Object.entries(q.tags || {}).slice(0,3).map(([k,v]) => <span key={k}>{k}: {String(v)}</span>)}</div></td><td className="date-cell">{q.created_at ? new Date(q.created_at).toLocaleDateString() : "—"}</td><td><StatusBadge status="unique"/></td></tr>)}</tbody></table></div>}
            </section>
          </>}

          {page === "add" && <>
            <SectionTitle eyebrow="KNOWLEDGE BASE" title="Add a question" description="Save a question only after it passes independent duplicate detection." icon={Plus}/>
            <section className="panel form-panel add-panel">
              <label>Question text</label>
              <textarea rows={5} value={newQuestion} onChange={e => setNewQuestion(e.target.value)} placeholder="Enter a clear educational question..."/>
              <label>Tags <span className="label-muted">JSON metadata</span></label>
              <textarea rows={3} value={newTags} onChange={e => setNewTags(e.target.value)} spellCheck="false"/>
              <div className="hint"><ShieldCheck size={14}/> Duplicate and review cases will not be saved.</div>
              <div className="form-actions"><button className="button button-secondary" onClick={() => setPage("bank")}>Cancel</button><button className="button button-primary" disabled={loading || !newQuestion.trim() || health !== "online"} onClick={saveQuestion}>{loading ? <LoaderCircle className="spin" size={17}/> : <Send size={16}/>} Save question</button></div>
            </section>
          </>}
          <footer className="page-footer"><span>QuestionIQ <span className="footer-dot">·</span> AI Question Generation & Duplicate Prevention</span><span><ShieldCheck size={14}/> Powered by Gemini and semantic embeddings</span></footer>
        </div>
      </main>
    </div>
  );
}

function LayersIcon() {
  return <Database size={23}/>;
}

function Metric({ icon: Icon, label, value, caption }) {
  return <div className="metric-card"><div className="metric-top"><span>{label}</span><div><Icon size={18}/></div></div><div className="metric-value">{value}</div><div className="metric-caption">{caption}</div></div>;
}

function Empty({ text }) {
  return <div className="empty-state"><div><BookOpen size={22}/></div><p>{text}</p></div>;
}
