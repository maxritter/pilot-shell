import { useRef, useState } from "react";
import {
  type ChangeAnchor,
  type ChangeCommentInput,
  checkId,
  newThreadId,
  type SharedReview,
  type SubmitResult,
} from "@/lib/sharing/sharing";

/**
 * The finished change, as a link reviewer sees it: what it proves (Overview),
 * how it was checked (Evidence) and how to try it. Comments only; the vote,
 * the files and the code stay with the team and the pull request.
 */

type Tab = "overview" | "evidence" | "try";
const TABS: [Tab, string][] = [
  ["overview", "Overview"],
  ["evidence", "Evidence"],
  ["try", "Try it"],
];

const REASONS: Record<Exclude<SubmitResult, { ok: true }>["reason"], string> = {
  gone: "This change is no longer shared, so it cannot take comments.",
  rate_limited: "Too many comments from this connection. Wait a few minutes and try again.",
  too_large: "That comment is too long. Shorten it and try again.",
  network: "The comment could not be sent. Check your connection and try again.",
};

/** Where a comment is, in words, the way the Cockpit labels it. */
function where(anchor: ChangeAnchor): string {
  if (anchor.kind === "doneMeans") return `Done means ${anchor.id}`;
  if (anchor.kind === "picture") return "A picture";
  return `Check ${anchor.id.replace(":", " ")}`;
}

type Sent = { thread: string; label: string; remark: string; replies: string[] };

function CommentOn({ anchor, onPick }: { anchor: ChangeAnchor; onPick: (a: ChangeAnchor) => void }) {
  return (
    <button type="button" className="sh-on" onClick={() => onPick(anchor)} aria-label={`Comment on ${where(anchor)}`}>
      Comment
    </button>
  );
}

function Picture({ review, file, caption, onPick }: { review: SharedReview; file: string; caption: string; onPick: (a: ChangeAnchor) => void }) {
  const src = review.images[file];
  // A picture that is missing or does not decode falls back to its file name; the caption stays.
  const [broken, setBroken] = useState(false);
  return (
    <figure className="sh-pic">
      {src !== undefined && !broken ? (
        <img src={src} alt={caption} loading="lazy" onError={() => setBroken(true)} />
      ) : (
        <div className="sh-pic-missing">{file}</div>
      )}
      <figcaption>
        {caption}
        <CommentOn anchor={{ kind: "picture", id: file, quote: caption }} onPick={onPick} />
      </figcaption>
    </figure>
  );
}

export function ChangeView({
  title,
  review,
  author,
  setAuthor,
  onComment,
}: {
  title: string;
  review: SharedReview;
  author: string;
  setAuthor: (name: string) => void;
  onComment: (input: ChangeCommentInput) => Promise<SubmitResult>;
}) {
  const [tab, setTab] = useState<Tab>("overview");
  const [anchor, setAnchor] = useState<ChangeAnchor | null>(null);
  const [replyTo, setReplyTo] = useState<Sent | null>(null);
  const [remark, setRemark] = useState("");
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState("");
  const [sent, setSent] = useState<Sent[]>([]);

  const box = useRef<HTMLTextAreaElement>(null);
  // Focusing the comment box also scrolls it into view where the panel sits below the change (phones).
  const pick = (a: ChangeAnchor) => {
    setReplyTo(null);
    setAnchor(a);
    box.current?.focus();
  };

  const send = async () => {
    const text = remark.trim();
    if (text === "" || (anchor === null && replyTo === null)) return;
    setBusy(true);
    setProblem("");
    const thread = replyTo?.thread ?? newThreadId();
    const input: ChangeCommentInput =
      replyTo !== null ? { author, remark: text, replyTo: replyTo.thread } : { author, remark: text, anchor: anchor as ChangeAnchor, thread };
    const result = await onComment(input);
    setBusy(false);
    if (result.ok === false) {
      setProblem(REASONS[result.reason]);
      return;
    }
    setSent(
      replyTo !== null
        ? sent.map((s) => (s.thread === replyTo.thread ? { ...s, replies: [...s.replies, text] } : s))
        : [...sent, { thread, label: where(anchor as ChangeAnchor), remark: text, replies: [] }],
    );
    setRemark("");
    setAnchor(null);
    setReplyTo(null);
  };

  const proven = review.doneMeans.filter((d) => d.proven).length;

  return (
    <div className="sh-layout">
      <article className="sh-plan sh-change">
        <header>
          <h1>{title}</h1>
          <p className="sh-note">
            Shared with you as a link: anyone who has it can read this change and comment on it. The code is reviewed in
            the pull request.
          </p>
          <p className="sh-verified">
            {review.verified ? "Checked" : "Not yet checked"}
            {review.round !== null ? ` in round ${review.round}` : ""} by an AI that did not write the code ·{" "}
            {proven} of {review.doneMeans.length} points proven
          </p>
          {review.pr !== null ? (
            <div className="sh-pr">
              <span className="sh-pr-num">{review.pr.number !== null ? `#${review.pr.number}` : "Pull request"}</span>
              <span className="sh-pr-title">{review.pr.title}</span>
              <span className="sh-pr-meta">
                {review.pr.state} · {review.pr.checks}
              </span>
              <a href={review.pr.url} target="_blank" rel="noopener noreferrer">
                Open on GitHub
              </a>
            </div>
          ) : null}
          <nav className="sh-tabs" aria-label="The change">
            {TABS.map(([id, label]) => (
              <button key={id} type="button" aria-current={id === tab ? "page" : undefined} onClick={() => setTab(id)}>
                {label}
              </button>
            ))}
          </nav>
        </header>

        {tab === "overview" ? (
          <section aria-label="What this change does">
            <h2>What this change does</h2>
            <ol className="sh-points">
              {review.doneMeans.map((d) => (
                <li key={d.n}>
                  <div className="sh-point-head">
                    <span className="sh-n">{d.n}</span>
                    <strong>{d.head}</strong>
                    <span className={d.proven ? "sh-tag ok" : "sh-tag"}>{d.proven ? "Proven" : "Not proven"}</span>
                    <CommentOn anchor={{ kind: "doneMeans", id: String(d.n), quote: d.head }} onPick={pick} />
                  </div>
                  {d.text !== "" ? <p>{d.text}</p> : null}
                  {d.proof !== "" ? <p className="sh-proof">Proof: {d.proof}</p> : null}
                  {d.evidence
                    .filter((file) => review.images[file] !== undefined)
                    .map((file) => (
                      <Picture
                        key={file}
                        review={review}
                        file={file}
                        caption={review.pictures.find((p) => p.file === file)?.caption ?? file}
                        onPick={pick}
                      />
                    ))}
                </li>
              ))}
            </ol>
            {review.notVerified.length > 0 ? (
              <>
                <h3>Not verified</h3>
                <ul>
                  {review.notVerified.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </>
            ) : null}
          </section>
        ) : null}

        {tab === "evidence" ? (
          <section aria-label="Evidence">
            <div className="sh-tiles">
              {review.tiles.map((t) => (
                <section key={t.key} className="sh-tile">
                  <h3>
                    {t.label}{" "}
                    <span className={t.passed === t.total ? "sh-tag ok" : "sh-tag"}>
                      {t.passed}/{t.total}
                    </span>
                  </h3>
                  <ul>
                    {t.lines.map((line) => (
                      <li key={line.label}>
                        <span aria-hidden="true">{line.ok ? "✓" : "✕"}</span> <span className="sh-line-label">{line.label}</span>{" "}
                        {line.text}
                        <CommentOn anchor={{ kind: "check", id: checkId(line.label), quote: line.text }} onPick={pick} />
                      </li>
                    ))}
                  </ul>
                </section>
              ))}
            </div>
            {review.pictures.length > 0 ? <h3>Pictures</h3> : null}
            {review.pictures.map((p) => (
              <Picture key={p.file} review={review} file={p.file} caption={p.caption} onPick={pick} />
            ))}
            {review.proofs.length > 0 ? (
              <>
                <h3>Other proofs</h3>
                <ul>
                  {review.proofs.map((p) => (
                    <li key={p.file}>
                      <strong>{p.title}</strong>: {p.caption}
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
            {review.second !== null ? (
              <details className="sh-second">
                <summary>
                  Second review by {review.second.name}
                  {review.second.findings !== null ? ` · ${review.second.findings} findings, answered by the agent` : ""}
                </summary>
                <p>An AI from another vendor reviewed the plan, the build record and the change. Its findings went to the agent.</p>
              </details>
            ) : null}
          </section>
        ) : null}

        {tab === "try" ? (
          <section aria-label="Try it">
            <h2>Try the whole change</h2>
            <p className="sh-note">Written by the AI that checked it, for whoever reviews.</p>
            <ol className="sh-steps">
              {review.tryIt.map((step) => (
                <li key={step.text}>
                  {step.text}
                  {step.command !== null ? <code>{step.command}</code> : null}
                </li>
              ))}
            </ol>
          </section>
        ) : null}
      </article>

      <aside className="sh-side" aria-label="Comments">
        <h2>Comment</h2>
        <label htmlFor="sh-author">Your name</label>
        <input id="sh-author" value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Guest" maxLength={80} />
        {anchor !== null || replyTo !== null ? (
          <blockquote className="sh-quote">
            {replyTo !== null ? `Reply on ${replyTo.label}` : `${where(anchor as ChangeAnchor)}${anchor?.quote ? `: ${anchor.quote}` : ""}`}
            <button
              type="button"
              onClick={() => {
                setAnchor(null);
                setReplyTo(null);
              }}
            >
              Cancel
            </button>
          </blockquote>
        ) : (
          <p className="sh-note">Choose Comment beside a point, a check or a picture.</p>
        )}
        <label htmlFor="sh-remark">Comment</label>
        <textarea id="sh-remark" ref={box} value={remark} onChange={(e) => setRemark(e.target.value)} rows={4} />
        {problem !== "" ? (
          <p className="sh-problem" role="alert">
            {problem}
          </p>
        ) : null}
        <div className="sh-actions">
          <button
            type="button"
            className="primary"
            disabled={busy || remark.trim() === "" || (anchor === null && replyTo === null)}
            onClick={() => void send()}
          >
            {replyTo !== null ? "Reply" : "Add comment"}
          </button>
        </div>
        {sent.length > 0 ? (
          <section className="sh-sent" aria-label="Sent">
            <h3>Sent to the owner</h3>
            {sent.map((s) => (
              <div key={s.thread} className="sh-thread">
                <p>
                  <strong>{s.label}</strong>: {s.remark}
                </p>
                {s.replies.map((r, i) => (
                  // Replies only ever append, so their position is their identity.
                  // biome-ignore lint/suspicious/noArrayIndexKey: append-only list
                  <p key={i} className="sh-reply">
                    {r}
                  </p>
                ))}
                <button
                  type="button"
                  className="sh-on"
                  onClick={() => {
                    setAnchor(null);
                    setReplyTo(s);
                    box.current?.focus();
                  }}
                >
                  Reply
                </button>
              </div>
            ))}
          </section>
        ) : null}
      </aside>
    </div>
  );
}
