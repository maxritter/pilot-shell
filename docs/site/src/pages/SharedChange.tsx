import { useState } from "react";
import { type ChangeAnchor, checkId, type SharedReview, where } from "@/lib/sharing/sharing";

/**
 * The finished change, under Build, as a link reviewer sees it: what it proves (Overview), how it
 * was checked (Evidence) and how to try it. Comments only; the vote, the files and the code stay
 * with the team and the pull request.
 */

type ChangeTab = "overview" | "evidence" | "try";
const TABS: [ChangeTab, string][] = [
  ["overview", "Overview"],
  ["evidence", "Evidence"],
  ["try", "Try it"],
];

function CommentOn({ anchor, onPick }: { anchor: ChangeAnchor; onPick: (a: ChangeAnchor) => void }) {
  return (
    <button type="button" className="sh-on" onClick={() => onPick(anchor)} aria-label={`Comment on ${where(anchor)}`}>
      Comment
    </button>
  );
}

function Picture({ review, file, caption, onPick }: { review: SharedReview; file: string; caption: string; onPick: (a: ChangeAnchor) => void }) {
  const src = review.images[file];
  // A picture that is missing or does not decode falls back to its caption alone.
  const [broken, setBroken] = useState(false);
  return (
    <figure className="sh-pic">
      {src !== undefined && !broken ? (
        <img src={src} alt={caption} loading="lazy" onError={() => setBroken(true)} />
      ) : (
        <div className="sh-pic-missing">Picture not included</div>
      )}
      <figcaption>
        <span>{caption}</span>
        <CommentOn anchor={{ kind: "picture", id: file, quote: caption }} onPick={onPick} />
      </figcaption>
    </figure>
  );
}

export function ChangeView({ review, onPick }: { review: SharedReview; onPick: (anchor: ChangeAnchor) => void }) {
  const [tab, setTab] = useState<ChangeTab>("overview");
  const proven = review.doneMeans.filter((d) => d.proven).length;

  return (
    <div className="sh-change">
      <p className="sh-check" data-testid="shared-checked">
        <span className="sh-mark check" aria-hidden="true" />
        {`${review.verified ? "Checked" : "Not yet checked"} by an agent that did not write the code · ${proven} of ${review.doneMeans.length} points proven`}
      </p>
      {review.pr !== null ? (
        <div className="sh-pr">
          <span className="sh-pr-num">{review.pr.number !== null ? `#${review.pr.number}` : "Pull request"}</span>
          <span className="sh-pr-title">{review.pr.title}</span>
          <span className="sh-pr-meta">{`${review.pr.state} · ${review.pr.checks}`}</span>
          <a href={review.pr.url} target="_blank" rel="noopener noreferrer">
            Open on GitHub
          </a>
        </div>
      ) : null}
      <nav className="sh-subtabs" aria-label="The change">
        {TABS.map(([id, label]) => (
          <button key={id} type="button" aria-current={id === tab ? "page" : undefined} onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </nav>

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
                  <CommentOn anchor={{ kind: "doneMeans", id: String(d.n), quote: d.head }} onPick={onPick} />
                </div>
                {d.text !== "" ? <p>{d.text}</p> : null}
                {d.proof !== "" ? <p className="sh-proof">{`Proof: ${d.proof}`}</p> : null}
                {d.evidence
                  .filter((file) => review.images[file] !== undefined)
                  .map((file) => (
                    <Picture
                      key={file}
                      review={review}
                      file={file}
                      caption={review.pictures.find((p) => p.file === file)?.caption ?? "Evidence"}
                      onPick={onPick}
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
                  <span className={t.passed === t.total ? "sh-tag ok" : "sh-tag"}>{`${t.passed}/${t.total}`}</span>
                </h3>
                <ul>
                  {t.lines.map((line) => (
                    <li key={line.label}>
                      <span className={line.ok ? "sh-mark done" : "sh-mark fail"} role="img" aria-label={line.ok ? "Passed" : "Failed"} />
                      <span className="sh-line-label">{line.label}</span> {line.text}
                      <CommentOn anchor={{ kind: "check", id: checkId(line.label), quote: line.text }} onPick={onPick} />
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
          {review.pictures.length > 0 ? <h3>Pictures</h3> : null}
          {review.pictures.map((p) => (
            <Picture key={p.file} review={review} file={p.file} caption={p.caption} onPick={onPick} />
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
                {`Second review by ${review.second.name}${review.second.findings !== null ? ` · ${review.second.findings} findings, answered by the agent` : ""}`}
              </summary>
              <p>An agent from another vendor read the plan, the build record and the change. Its findings went to the agent.</p>
            </details>
          ) : null}
        </section>
      ) : null}

      {tab === "try" ? (
        <section aria-label="Try it">
          <h2>Try the whole change</h2>
          <p className="sh-note">Written by the agent that checked it, for whoever reviews.</p>
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
    </div>
  );
}
