import { Fragment, useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useLocation, useParams } from "react-router-dom";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import { addRemark, answerItem, type Drafts, EMPTY, pending, removeRemark, summary } from "@/lib/sharing/drafts";
import { contractsOf, mockupName, planBlocks, slicesOf } from "@/lib/sharing/plan";
import { watchShare } from "@/lib/sharing/poll";
import {
  type ChangeAnchor,
  type GuestAnswer,
  type LoadedShare,
  linkKeyOf,
  newThreadId,
  type Remark,
  type ShareItem,
  type SubmitResult,
  stepDocs,
  submitRemarks,
  type Tab,
  tabOfStep,
  where,
} from "@/lib/sharing/sharing";
import { Asks } from "./shared/Asks";
import { Blocks } from "./shared/Blocks";
import { ChangeView } from "./SharedChange";
import "@/styles/shared.css";

const NAME_KEY = "qualitylayer-guest-name";

function storedName(): string {
  try {
    return typeof window === "undefined" ? "" : (window.localStorage.getItem(NAME_KEY) ?? "");
  } catch {
    return "";
  }
}

const REASONS: Record<Exclude<SubmitResult, { ok: true }>["reason"], string> = {
  gone: "This plan is no longer shared, so it cannot take comments.",
  rate_limited: "Too many comments from this connection. Wait a few minutes and try again.",
  too_large: "A comment is too long. Shorten it and try again.",
  network: "It could not be sent. Check your connection and try again.",
};

const TABS: [Tab, string][] = [
  ["discuss", "Discuss"],
  ["plan", "Plan"],
  ["implement", "Implement"],
  ["verify", "Verify"],
  ["review", "Review"],
];

/** What a step with nothing in this link says, in one sentence. */
const NOT_THERE: Record<Tab, string> = {
  discuss: "The conversation that settled the problem is not part of this link.",
  plan: "The Plan is not written yet. It appears here once it waits for approval.",
  implement: "The build has not started. Its progress appears here when it does.",
  verify: "Verification has not started. The checks appear here when it does.",
  review: "The review is not ready yet. The result appears here when it is.",
};

/** The file a comment on a step's text is recorded against when the link names none. */
const DEFAULT_DOC: Record<Tab, string> = { discuss: "00-discuss.md", plan: "02-plan.md", implement: "03-implement.md", verify: "04-verify.md", review: "05-review.md" };

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

/** Text with `code` spans drawn as code. */
const Inline = ({ text }: { text: string }) => (
  <>
    {text.split(/(`[^`]+`)/).map((part, i) => (
      // The parts never reorder, so their position is their identity.
      // biome-ignore lint/suspicious/noArrayIndexKey: static split
      <Fragment key={i}>{part.startsWith("`") && part.endsWith("`") && part.length > 2 ? <code>{part.slice(1, -1)}</code> : part}</Fragment>
    ))}
  </>
);

/** Where the next comment goes: a quoted passage (or none), a point of the change, or a reply. */
type Target = { kind: "passage"; quote: string; doc?: string } | { kind: "anchor"; anchor: ChangeAnchor } | { kind: "reply"; thread: string; label: string };

/** A comment that was sent, kept on the page so the reviewer sees what the owner got. */
type SentComment = { key: string; thread?: string; label: string; text: string; replies: string[] };

const labelOf = (r: Exclude<Remark, { kind: "item" }>): string =>
  r.kind === "passage" ? (r.quote !== "" ? `“${r.quote.length > 80 ? `${r.quote.slice(0, 80)}…` : r.quote}”` : "General comment") : r.kind === "thread" ? where(r.anchor) : "Reply";

type ReadyShare = Extract<LoadedShare, { status: "ready" }>;

function firstTab(share: ReadyShare, steps: Record<Tab, string[]>): Tab {
  if (share.review !== undefined) return "review";
  return (["plan", "discuss", "implement", "verify", "review"] as const).find((tab) => steps[tab].length > 0) ?? "plan";
}

function Sections({ share, names, items, drafts, settled, onAnswer }: {
  share: ReadyShare;
  names: string[];
  items: ShareItem[];
  drafts: Drafts;
  settled: Record<string, string>;
  onAnswer: (id: string, answer: GuestAnswer | null, note?: string) => void;
}) {
  const details = names.filter((n) => /-details\.md$/.test(n));
  const main = names.filter((n) => !details.includes(n));
  const detailText = details.map((n) => share.docs[n] ?? "").join("\n\n");
  const slices = slicesOf(detailText);
  const tasks = slices.reduce((sum, s) => sum + s.tasks, 0);
  const contracts = contractsOf(detailText);
  // A mockup that is a question is drawn there; the plan's own fence for it would draw it twice.
  const shown = new Set(items.flatMap((i) => (i.media?.kind === "artifact" ? [mockupName(i.media.name)] : [])));
  return (
    <>
      <Asks items={items} owner={share.owner} docs={share.docs} stills={share.stills} drafts={drafts} settled={settled} onAnswer={onAnswer} />
      {main.map((name) => (
        // The document a selected passage is in, so a comment is filed against it.
        <div key={name} className="sh-docs" data-doc={name}>
          <Blocks blocks={planBlocks(share.docs[name] ?? "")} docs={share.docs} stills={share.stills} shown={shown} />
        </div>
      ))}
      {slices.length > 0 ? (
        <section className="sh-sec" aria-label="The build">
          <h2>{`The build · ${plural(slices.length, "slice", "slices")}, ${plural(tasks, "task", "tasks")}`}</h2>
          <ol className="sh-slices">
            {slices.map((s) => (
              <li key={s.n}>
                <span className="sh-num">{s.n}</span>
                <span className="sh-slice-t">
                  <Inline text={s.title} />
                </span>
                <span className="sh-slice-r">{plural(s.tasks, "task", "tasks")}</span>
              </li>
            ))}
          </ol>
        </section>
      ) : null}
      {contracts.length > 0 ? (
        <details className="sh-fold" data-doc={details[0]}>
          <summary>
            <span className="sh-mark todo" aria-hidden="true" />
            <b>Contracts</b>
            <span className="sh-fold-line">{`${plural(contracts.length, "interface", "interfaces")} the build must keep, with their diffs`}</span>
            <span className="sh-chev" aria-hidden="true" />
          </summary>
          <div className="sh-fold-body">
            {contracts.map((c) => (
              <section key={c.title} className="sh-contract">
                <h3>
                  <Inline text={c.title} />
                </h3>
                <Blocks blocks={planBlocks(c.body)} docs={share.docs} />
              </section>
            ))}
          </div>
        </details>
      ) : null}
    </>
  );
}

/** A shared task: Discuss, Plan and Build, the owner's questions, and a place to answer and comment. */
function Ready({
  share,
  initialTab,
  onSend,
}: {
  share: ReadyShare;
  initialTab?: Tab;
  onSend: (author: string, remarks: Remark[]) => Promise<SubmitResult>;
}) {
  const steps = stepDocs(share.docs);
  const [tab, setTab] = useState<Tab>(initialTab ?? firstTab(share, steps));
  const [author, setAuthor] = useState(storedName);
  const [drafts, setDrafts] = useState<Drafts>(EMPTY);
  const [settled, setSettled] = useState<Record<string, string>>({});
  const [sent, setSent] = useState<SentComment[]>([]);
  const [target, setTarget] = useState<Target>({ kind: "passage", quote: "" });
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState("");
  const [delivered, setDelivered] = useState(false);
  const box = useRef<HTMLTextAreaElement>(null);
  const nameBox = useRef<HTMLInputElement>(null);
  const [askedName, setAskedName] = useState(false);

  const who = share.owner ?? "the owner";
  const items = share.items;
  const drafted = summary(drafts, items);
  // What was sent still counts as answered.
  const counts = { ...drafted, answered: drafted.answered + items.filter((item) => settled[item.id] !== undefined).length };
  const waiting = pending(drafts, items, share.docs);
  const expires = share.expires === undefined ? null : new Date(share.expires);
  const hasChange = share.review !== undefined;
  // On the change a comment belongs to a point of it; on a document it may be a general remark.
  const needsPoint = tab === "review" && hasChange && target.kind === "passage";

  const answer = (id: string, a: GuestAnswer | null, note?: string) => {
    setDelivered(false);
    setDrafts((d) => answerItem(d, id, a, note));
  };

  const pick = (anchor: ChangeAnchor) => {
    setTarget({ kind: "anchor", anchor });
    box.current?.focus();
  };

  const add = () => {
    const remark: Drafts["remarks"][number] =
      target.kind === "passage"
        ? { kind: "passage", doc: target.doc ?? steps[tab][0] ?? DEFAULT_DOC[tab], quote: target.quote, text }
        : target.kind === "anchor"
          ? { kind: "thread", thread: newThreadId(), anchor: target.anchor, text }
          : { kind: "reply", thread: target.thread, text };
    setDelivered(false);
    setDrafts((d) => addRemark(d, remark));
    setText("");
    setTarget({ kind: "passage", quote: "" });
  };

  const send = async () => {
    if (waiting.length === 0) return;
    // Below the page (a phone), the name field is out of sight: ask for it once, where it is, before sending as Guest.
    const field = nameBox.current;
    if (author.trim() === "" && !askedName && field !== null) {
      const { top, bottom } = field.getBoundingClientRect();
      if (top < 0 || bottom > window.innerHeight) {
        setAskedName(true);
        field.scrollIntoView({ block: "center" });
        field.focus({ preventScroll: true });
        return;
      }
    }
    setBusy(true);
    setProblem("");
    const result = await onSend(author, waiting);
    setBusy(false);
    if (result.ok === false) {
      setProblem(REASONS[result.reason]);
      return;
    }
    try {
      window.localStorage.setItem(NAME_KEY, author.trim());
    } catch {
      // the name is a convenience only
    }
    setSettled((s) => ({ ...s, ...Object.fromEntries(waiting.flatMap((r) => (r.kind === "item" ? [[r.id, r.label]] : []))) }));
    setSent((list) => {
      let next = list;
      for (const r of waiting) {
        if (r.kind === "item") continue;
        if (r.kind === "reply") next = next.map((c) => (c.thread === r.thread ? { ...c, replies: [...c.replies, r.text] } : c));
        else next = [...next, { key: `${next.length}`, thread: r.kind === "thread" ? r.thread : undefined, label: labelOf(r), text: r.text, replies: [] }];
      }
      return next;
    });
    setDrafts(EMPTY);
    setDelivered(true);
  };

  const names = steps[tab];
  const tabItems = items.filter((item) => tabOfStep(item.step) === tab);
  const count = `${counts.total > 0 ? `${counts.answered} of ${counts.total} answered · ` : ""}${plural(counts.comments, "comment", "comments")}`;

  return (
    <div className="sh-layout">
      <article className="sh-main">
        <header>
          <h1>{share.title}</h1>
          <p className="sh-meta">
            {`${share.owner !== undefined ? `${share.owner} shared this with you` : "Shared with you"} to read and comment on${
              expires !== null ? ` · the link runs out on ${expires.toLocaleDateString("en-US", { day: "numeric", month: "short" })}` : ""
            } · no code is shared`}
          </p>
          <nav className="sh-tabs" aria-label="Steps">
            {TABS.map(([id, label]) => (
              <button key={id} type="button" aria-current={id === tab ? "page" : undefined} onClick={() => setTab(id)}>
                {label}
              </button>
            ))}
          </nav>
        </header>

        {/* biome-ignore lint/a11y/noStaticElementInteractions: selecting text is how a passage is quoted */}
        <div
          className="sh-body"
          data-testid="shared-doc"
          onMouseUp={() => {
            const picked = window.getSelection()?.toString().trim() ?? "";
            if (picked === "") return;
            const node = window.getSelection()?.anchorNode;
            const from = node instanceof Element ? node : node?.parentElement;
            setTarget({ kind: "passage", quote: picked.slice(0, 1000), doc: from?.closest<HTMLElement>("[data-doc]")?.dataset.doc });
          }}
        >
          {tab === "review" && hasChange ? (
            <>
              <Sections share={share} names={names} items={tabItems} drafts={drafts} settled={settled} onAnswer={answer} />
              <ChangeView review={share.review as NonNullable<typeof share.review>} onPick={pick} />
            </>
          ) : names.length > 0 || tabItems.length > 0 ? (
            <Sections share={share} names={names} items={tabItems} drafts={drafts} settled={settled} onAnswer={answer} />
          ) : (
            <p className="sh-empty">{NOT_THERE[tab]}</p>
          )}
        </div>
      </article>

      <aside className="sh-side" aria-label="Your answers and comments">
        <section className="sh-card">
          <label htmlFor="sh-author">
            <b>Your name</b>
          </label>
          <input id="sh-author" ref={nameBox} value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Guest" maxLength={80} autoComplete="name" />
          <span className="sh-hint">
            {askedName && author.trim() === ""
              ? "Add a name so the owner knows who wrote this, or press Send again to send as Guest."
              : "Shown next to your comments. No account needed."}
          </span>
        </section>

        <section className="sh-card" aria-label="Comment">
          <label htmlFor="sh-remark">
            <b>Comment</b>
          </label>
          {target.kind === "passage" && target.quote !== "" ? (
            <blockquote className="sh-quote">
              {target.quote}
              <button type="button" onClick={() => setTarget({ kind: "passage", quote: "" })}>
                Drop quote
              </button>
            </blockquote>
          ) : target.kind === "anchor" || target.kind === "reply" ? (
            <blockquote className="sh-quote">
              {target.kind === "reply" ? `Reply on ${target.label}` : `${where(target.anchor)}${target.anchor.quote ? `: ${target.anchor.quote}` : ""}`}
              <button type="button" onClick={() => setTarget({ kind: "passage", quote: "" })}>
                Cancel
              </button>
            </blockquote>
          ) : (
            <span className="sh-hint">
              {needsPoint ? "Choose Comment beside a point, a check or a picture." : "Select a passage to comment on it, or leave a general remark."}
            </span>
          )}
          <textarea id="sh-remark" ref={box} value={text} onChange={(e) => setText(e.target.value)} rows={4} />
          <div className="sh-row">
            <button type="button" className="sh-btn" disabled={text.trim() === "" || needsPoint} onClick={add}>
              Add comment
            </button>
          </div>
          {drafts.remarks.length > 0 ? (
            <ul className="sh-drafts" aria-label="Comments not sent yet">
              {drafts.remarks.map((r, i) => (
                // A draft is told apart by its place in the list, and only removal reorders it.
                // biome-ignore lint/suspicious/noArrayIndexKey: removal re-keys the rest
                <li key={i}>
                  <span className="sh-draft-label">{labelOf(r)}</span>
                  <span>{r.text}</span>
                  <button type="button" className="sh-link" onClick={() => setDrafts((d) => removeRemark(d, i))}>
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </section>

        <section className="sh-card sh-done" aria-label="Send">
          <b>When you are done</b>
          <span>{count}</span>
          {problem !== "" ? (
            <p className="sh-problem" role="alert">
              {problem}
            </p>
          ) : null}
          <div className="sh-row">
            <button type="button" className="sh-btn p" disabled={busy || waiting.length === 0} onClick={() => void send()}>
              {`Send to ${who}`}
            </button>
          </div>
          {delivered ? (
            <p className="sh-delivered" role="status">
              {`Sent to ${who}.`}
            </p>
          ) : null}
          <span className="sh-hint">{`Approving is for ${who}'s team, in the App.`}</span>
          {sent.length > 0 ? (
            <div className="sh-sent" aria-label="Sent">
              <h3>{`Sent to ${who}`}</h3>
              {sent.map((c) => (
                <div key={c.key} className="sh-thread">
                  <p>
                    <strong>{c.label}</strong>: {c.text}
                  </p>
                  {c.replies.map((r, i) => (
                    // Replies only ever append, so their position is their identity.
                    // biome-ignore lint/suspicious/noArrayIndexKey: append-only list
                    <p key={i} className="sh-reply">
                      {r}
                    </p>
                  ))}
                  {c.thread !== undefined ? (
                    <button
                      type="button"
                      className="sh-link"
                      onClick={() => {
                        setTarget({ kind: "reply", thread: c.thread as string, label: c.label });
                        box.current?.focus();
                      }}
                    >
                      Reply
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </aside>

      {waiting.length > 0 ? (
        <div className="sh-bar">
          <span>{count}</span>
          <button type="button" className="sh-btn p" disabled={busy} onClick={() => void send()}>
            {`Send to ${who}`}
          </button>
        </div>
      ) : null}
    </div>
  );
}

/** What the page shows for each state of the link; a plain function of its state. */
export function SharedView({
  state,
  onSend,
  tab,
}: {
  state: LoadedShare | { status: "loading" };
  onSend: (author: string, remarks: Remark[]) => Promise<SubmitResult>;
  /** The step to open on; the first one with something in it when absent. */
  tab?: Tab;
}) {
  if (state.status === "loading") return <p className="sh-status">Loading the plan…</p>;
  if (state.status === "gone") {
    return (
      <div className="sh-status">
        <h1>This plan is no longer shared</h1>
        <p>The owner stopped sharing it, or the link ran out. Ask them for a new link.</p>
      </div>
    );
  }
  if (state.status === "no-key") {
    return (
      <div className="sh-status">
        <h1>This link is missing its key</h1>
        <p>
          The plan is encrypted, and the key is the part of the link after the “#”. Ask the owner for the whole link,
          or copy it again with everything up to the end.
        </p>
      </div>
    );
  }
  if (state.status === "error") {
    return (
      <div className="sh-status">
        <h1>The plan could not be opened</h1>
        <p>{state.message}</p>
      </div>
    );
  }
  return <Ready share={state} initialTab={tab} onSend={onSend} />;
}

/** One link's page; keyed by the id and key, so another link starts from "loading" again. */
export const SharedLink = ({ id, linkKey }: { id: string; linkKey: string }) => {
  const [state, setState] = useState<LoadedShare | { status: "loading" }>({ status: "loading" });
  const [problem, setProblem] = useState<string | null>(null);

  useEffect(() => watchShare(id, linkKey, setState, setProblem), [id, linkKey]);

  return <>{problem !== null ? <p className="sh-hint" role="status">{problem}</p> : null}<SharedView state={state} onSend={(author, remarks) => submitRemarks(id, linkKey, author, remarks)} /></>;
};

const Shared = () => {
  const { id = "" } = useParams<{ id?: string }>();
  // The key is the link's fragment: the browser never sends it to the server.
  const key = linkKeyOf(useLocation().hash);
  return (
    <Page className="sh-page">
      <SEO title="A shared plan — QualityLayer" description="A plan shared with you from QualityLayer. Read it and comment on it." />
      <Helmet>
        <meta name="robots" content="noindex" />
      </Helmet>
      <SharedLink key={`${id}#${key}`} id={id} linkKey={key} />
    </Page>
  );
};

export default Shared;
