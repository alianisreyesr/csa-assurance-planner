import { FormEvent, useEffect, useState } from "react";
import { api, ApiError } from "./api";
import type {
  Assessment,
  AssuranceItem,
  AuditEntry,
  Review,
  Summary,
} from "./types";

type Tab = "dashboard" | "assessments" | "new" | "audit";

const ACTOR_KEY = "csa-actor";

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const [actor, setActor] = useState(() => localStorage.getItem(ACTOR_KEY) || "A.Reyes");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    localStorage.setItem(ACTOR_KEY, actor);
  }, [actor]);

  return (
    <div className="app">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <header className="topbar">
        <div>
          <h1>CSA Assurance Planner</h1>
          <p className="subtitle">Risk-based planning · synthetic records only</p>
        </div>
        <nav className="nav" aria-label="Main navigation">
          {(
            [
              ["dashboard", "Dashboard"],
              ["assessments", "Assessments"],
              ["new", "New plan"],
              ["audit", "Audit log"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              className={tab === key ? "active" : ""}
              aria-current={tab === key ? "page" : undefined}
              onClick={() => {
                if (key === "assessments") setSelectedId(null);
                setTab(key);
              }}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>
      <div className="banner" role="note">
        Portfolio prototype — every assessment, item, and actor is fictional. This is not validated CSA software.
      </div>
      <div className="actor-bar">
        <label htmlFor="actor">
          X-Actor (audit header, not login)
          <input
            id="actor"
            value={actor}
            onChange={(e) => setActor(e.target.value)}
            maxLength={80}
          />
        </label>
      </div>
      <main className="main" id="main-content">
        {tab === "dashboard" && (
          <Dashboard onOpen={(id) => { setSelectedId(id); setTab("assessments"); }} />
        )}
        {tab === "assessments" &&
          (selectedId ? (
            <AssessmentDetail
              id={selectedId}
              actor={actor}
              onBack={() => setSelectedId(null)}
            />
          ) : (
            <AssessmentList onSelect={setSelectedId} />
          ))}
        {tab === "new" && (
          <NewAssessmentForm
            actor={actor}
            onCreated={(id) => {
              setSelectedId(id);
              setTab("assessments");
            }}
          />
        )}
        {tab === "audit" && <AuditLog />}
      </main>
    </div>
  );
}

function Dashboard({ onOpen }: { onOpen: (id: number) => void }) {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [rows, setRows] = useState<Assessment[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.summary(), api.listAssessments()])
      .then(([s, list]) => {
        setSummary(s);
        setRows(list);
      })
      .catch((err: ApiError) => setError(err.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!summary) return <p className="muted">Loading summary…</p>;

  return (
    <>
      <div className="cards">
        <Stat label="Assessments" value={summary.total_assessments} />
        <Stat label="High risk" value={summary.high_risk_count} />
        <Stat label="Assurance items" value={summary.assurance_items} />
        <Stat label="Approved reviews" value={summary.approved_reviews} />
      </div>
      <section className="section">
        <h2>Recent assessments</h2>
        <AssessmentTable rows={rows.slice(0, 8)} onSelect={onOpen} />
      </section>
    </>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <article className="card">
      <div className="value">{value}</div>
      <div className="label">{label}</div>
    </article>
  );
}

function AssessmentList({ onSelect }: { onSelect: (id: number) => void }) {
  const [rows, setRows] = useState<Assessment[]>([]);
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listAssessments(status || undefined)
      .then(setRows)
      .catch((err: ApiError) => setError(err.message));
  }, [status]);

  return (
    <section className="section">
      <h2>Assessments</h2>
      <div className="filters">
        <label htmlFor="status-filter">
          Status
          <select id="status-filter" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All</option>
            <option value="planned">planned</option>
            <option value="in_review">in_review</option>
            <option value="approved">approved</option>
          </select>
        </label>
      </div>
      {error && <p className="error">{error}</p>}
      <AssessmentTable rows={rows} onSelect={onSelect} />
    </section>
  );
}

function AssessmentTable({
  rows,
  onSelect,
}: {
  rows: Assessment[];
  onSelect: (id: number) => void;
}) {
  if (!rows.length) return <p className="muted">No assessments yet.</p>;
  return (
    <table>
      <thead>
        <tr>
          <th scope="col">Ref</th>
          <th scope="col">Title</th>
          <th scope="col">System</th>
          <th scope="col">Risk</th>
          <th scope="col">Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <th scope="row">
              <button type="button" className="link" onClick={() => onSelect(row.id)}>
                {row.assessment_ref}
              </button>
            </th>
            <td>{row.title}</td>
            <td>{row.system_name}</td>
            <td>
              <span className={`badge ${row.risk_level}`}>{row.risk_level}</span>
            </td>
            <td>{row.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function AssessmentDetail({
  id,
  actor,
  onBack,
}: {
  id: number;
  actor: string;
  onBack: () => void;
}) {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [items, setItems] = useState<AssuranceItem[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [error, setError] = useState<string | null>(null);

  function reload() {
    Promise.all([api.getAssessment(id), api.listItems(id), api.listReviews(id)])
      .then(([a, i, r]) => {
        setAssessment(a);
        setItems(i);
        setReviews(r);
      })
      .catch((err: ApiError) => setError(err.message));
  }

  useEffect(reload, [id]);

  async function onAddItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries()) as Record<string, string>;
    try {
      await api.addItem(id, data, actor);
      form.reset();
      reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to add item");
    }
  }

  async function onAddReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries()) as Record<string, string>;
    try {
      await api.addReview(id, data, actor);
      form.reset();
      reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to add review");
    }
  }

  if (!assessment) return error ? <p className="error">{error}</p> : <p className="muted">Loading…</p>;

  return (
    <>
      <button type="button" className="link" onClick={onBack}>
        ← Back to list
      </button>
      <section className="section">
        <h2>
          {assessment.assessment_ref} · {assessment.title}
        </h2>
        <p>
          <span className={`badge ${assessment.risk_level}`}>{assessment.risk_level}</span>{" "}
          GAMP {assessment.gamp_category} · {assessment.system_name} · {assessment.status}
        </p>
        <p>{assessment.intended_use}</p>
        <p className="muted">
          Opened by {assessment.created_by} at {assessment.created_at}
        </p>
      </section>

      {error && <p className="error">{error}</p>}

      <section className="section">
        <h2>Assurance items</h2>
        {items.length ? (
          <table>
            <thead>
              <tr>
                <th scope="col">Req</th>
                <th scope="col">Function</th>
                <th scope="col">Class</th>
                <th scope="col">Strategy</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <th scope="row">{item.requirement_ref}</th>
                  <td>{item.function_name}</td>
                  <td>
                    <span className="badge ok">{item.csa_class}</span>
                  </td>
                  <td>{item.test_strategy}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">No items yet.</p>
        )}
        <form onSubmit={onAddItem}>
          <legend>Add item</legend>
          <label>
            Requirement ref
            <input name="requirement_ref" required minLength={2} maxLength={40} />
          </label>
          <label>
            Function name
            <input name="function_name" required minLength={3} maxLength={200} />
          </label>
          <label>
            CSA class
            <select name="csa_class" defaultValue="critical_thinking">
              <option value="scripted">scripted</option>
              <option value="unscripted">unscripted</option>
              <option value="critical_thinking">critical_thinking</option>
              <option value="record">record</option>
              <option value="signature">signature</option>
            </select>
          </label>
          <label>
            Rationale
            <textarea name="rationale" required minLength={10} maxLength={500} />
          </label>
          <label>
            Test strategy
            <textarea name="test_strategy" required minLength={10} maxLength={500} />
          </label>
          <button type="submit" className="primary">
            Add assurance item
          </button>
        </form>
      </section>

      <section className="section">
        <h2>Reviews</h2>
        <ul className="timeline">
          {reviews.map((review) => (
            <li key={review.id}>
              <span className="actor">{review.reviewer}</span>{" "}
              <span className={`badge ${review.decision === "approve" ? "ok" : "gap"}`}>
                {review.decision}
              </span>
              <div>{review.comment}</div>
              <div className="time">{review.reviewed_at}</div>
            </li>
          ))}
        </ul>
        <form onSubmit={onAddReview}>
          <legend>Record review</legend>
          <label>
            Reviewer
            <input name="reviewer" required minLength={2} maxLength={80} defaultValue={actor} />
          </label>
          <label>
            Decision
            <select name="decision" defaultValue="approve">
              <option value="approve">approve</option>
              <option value="needs_revision">needs_revision</option>
            </select>
          </label>
          <label>
            Comment
            <textarea name="comment" maxLength={500} />
          </label>
          <button type="submit" className="primary">
            Save review
          </button>
        </form>
      </section>
    </>
  );
}

function NewAssessmentForm({
  actor,
  onCreated,
}: {
  actor: string;
  onCreated: (id: number) => void;
}) {
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries()) as Record<
      string,
      string
    >;
    try {
      const created = await api.createAssessment(data, actor);
      onCreated(created.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create assessment");
    }
  }

  return (
    <section className="section">
      <h2>New CSA assessment</h2>
      <p className="muted">Describe intended use and risk. Do not enter real system names from a regulated site.</p>
      {error && <p className="error">{error}</p>}
      <form onSubmit={onSubmit}>
        <label>
          Title
          <input name="title" required minLength={3} maxLength={200} />
        </label>
        <label>
          System name
          <input name="system_name" required minLength={2} maxLength={100} />
        </label>
        <label>
          GAMP category
          <select name="gamp_category" defaultValue="4">
            <option value="1">1</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </label>
        <label>
          Risk level
          <select name="risk_level" defaultValue="medium">
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>
        <label>
          Intended use
          <textarea name="intended_use" required minLength={10} maxLength={500} />
        </label>
        <label>
          Created by
          <input name="created_by" required minLength={2} maxLength={80} defaultValue={actor} />
        </label>
        <button type="submit" className="primary">
          Create assessment
        </button>
      </form>
    </section>
  );
}

function AuditLog() {
  const [rows, setRows] = useState<AuditEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.auditLog().then(setRows).catch((err: ApiError) => setError(err.message));
  }, []);

  if (error) return <p className="error">{error}</p>;

  return (
    <section className="section">
      <h2>Application audit log</h2>
      <p className="muted">Append-oriented events with server-generated UTC timestamps.</p>
      <ul className="timeline">
        {rows.map((row) => (
          <li key={row.id}>
            <span className="actor">{row.actor}</span> {row.action}
            {row.detail ? ` — ${row.detail}` : ""}
            <div className="time">{row.created_at}</div>
          </li>
        ))}
      </ul>
    </section>
  );
}
