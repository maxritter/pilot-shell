import DOMPurify from "dompurify";
import { marked } from "marked";
import { useEffect, useRef, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useParams } from "react-router-dom";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import {
  type ChangeCommentInput,
  type CommentInput,
  type LoadedShare,
  loadShare,
  orderedDocs,
  type SubmitResult,
  submitChangeComment,
  submitComment,
} from "@/lib/sharing/sharing";
import { mermaidRenderer, renderDiagrams } from "@/lib/sharing/diagrams";
import { ChangeView } from "./SharedChange";
import "@/styles/shared.css";

const NAME_KEY = "qualitylayer-guest-name";

const escapeHtml = (text: string) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/** A plan's markdown as safe HTML. Without a DOM to sanitise with, the text is shown as text. */
function renderMarkdown(markdown: string): string {
  if (typeof window === "undefined") return `<pre>${escapeHtml(markdown)}</pre>`;
  return DOMPurify.sanitize(marked.parse(markdown, { async: false }) as string, {
    FORBID_TAGS: ["style", "iframe", "form", "object", "embed"],
    FORBID_ATTR: ["style", "onerror", "onclick"],
  });
}

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
  too_large: "That comment is too long. Shorten it and try again.",
  network: "The comment could not be sent. Check your connection and try again.",
};

type Sent = { quote: string; remark: string; verdict?: string };

type ReadyShare = Extract<LoadedShare, { status: "ready" }>;

/** A shared task: the finished change when it got that far, and the plan behind it. */
function Ready({
  share,
  onComment,
  onChangeComment,
}: {
  share: ReadyShare;
  onComment: (input: CommentInput) => Promise<SubmitResult>;
  onChangeComment: (input: ChangeCommentInput) => Promise<SubmitResult>;
}) {
  const [author, setAuthor] = useState(storedName);
  const hasPlan = orderedDocs(share.docs).length > 0;
  const [view, setView] = useState<"change" | "plan">(share.review !== undefined ? "change" : "plan");
  const remember = (name: string) => {
    setAuthor(name);
    try {
      window.localStorage.setItem(NAME_KEY, name.trim());
    } catch {
      // the name is a convenience only
    }
  };
  if (share.review === undefined) return <Plan share={share} author={author} setAuthor={setAuthor} onComment={onComment} />;
  return (
    <>
      {hasPlan ? (
        <nav className="sh-switch" aria-label="What to read">
          <button type="button" aria-current={view === "change" ? "page" : undefined} onClick={() => setView("change")}>
            The change
          </button>
          <button type="button" aria-current={view === "plan" ? "page" : undefined} onClick={() => setView("plan")}>
            The plan
          </button>
        </nav>
      ) : null}
      {view === "change" ? (
        <ChangeView
          title={share.title}
          review={share.review}
          author={author}
          setAuthor={remember}
          onComment={onChangeComment}
        />
      ) : (
        <Plan share={share} author={author} setAuthor={setAuthor} onComment={onComment} />
      )}
    </>
  );
}

function Plan({
  share,
  author,
  setAuthor,
  onComment,
}: {
  share: ReadyShare;
  author: string;
  setAuthor: (name: string) => void;
  onComment: (input: CommentInput) => Promise<SubmitResult>;
}) {
  const names = orderedDocs(share.docs);
  const [doc, setDoc] = useState(names[0] ?? "");
  const docRef = useRef<HTMLDivElement>(null);
  // The site is dark; diagrams are drawn after the document is on the page.
  useEffect(() => {
    if (docRef.current !== null) void renderDiagrams(docRef.current, mermaidRenderer(true));
  }, [doc, share]);
  const [quote, setQuote] = useState("");
  const [remark, setRemark] = useState("");
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState("");
  const [sent, setSent] = useState<Sent[]>([]);

  const send = async (verdict?: CommentInput["verdict"]) => {
    if (remark.trim() === "" && verdict === undefined) return;
    setBusy(true);
    setProblem("");
    const result = await onComment({ author, doc, quote, remark, verdict });
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
    setSent([...sent, { quote, remark: remark.trim(), verdict }]);
    setQuote("");
    setRemark("");
  };

  const expires = share.expires === undefined ? null : new Date(share.expires);

  return (
    <div className="sh-layout">
      <article className="sh-plan">
        <header>
          <h1>{share.title}</h1>
          <p className="sh-note">
            Shared with you as a link: anyone who has it can read this plan and comment on it.
            {expires !== null
              ? ` The link runs out on ${expires.toLocaleDateString(undefined, { day: "numeric", month: "short" })}.`
              : ""}
          </p>
          {names.length > 1 ? (
            <nav className="sh-tabs" aria-label="Documents">
              {names.map((name) => (
                <button
                  key={name}
                  type="button"
                  aria-current={name === doc ? "page" : undefined}
                  onClick={() => setDoc(name)}
                >
                  {name.replace(/\.md$/, "")}
                </button>
              ))}
            </nav>
          ) : null}
        </header>
        {/* biome-ignore lint/a11y/noStaticElementInteractions: selecting text is how a passage is quoted */}
        <div
          className="sh-doc"
          data-testid="shared-doc"
          ref={docRef}
          onMouseUp={() => {
            const picked = window.getSelection()?.toString().trim() ?? "";
            if (picked !== "") setQuote(picked.slice(0, 1000));
          }}
          // The markdown is sanitised above (or escaped when there is no DOM).
          // biome-ignore lint/security/noDangerouslySetInnerHtml: sanitised by renderMarkdown
          dangerouslySetInnerHTML={{ __html: renderMarkdown(share.docs[doc] ?? "") }}
        />
      </article>

      <aside className="sh-side" aria-label="Comments">
        <h2>Comment</h2>
        <label htmlFor="sh-author">Your name</label>
        <input id="sh-author" value={author} onChange={(e) => setAuthor(e.target.value)} placeholder="Guest" maxLength={80} />
        {quote !== "" ? (
          <blockquote className="sh-quote">
            {quote}
            <button type="button" onClick={() => setQuote("")}>
              Drop quote
            </button>
          </blockquote>
        ) : (
          <p className="sh-note">Select a passage to comment on it, or leave a general remark.</p>
        )}
        <label htmlFor="sh-remark">Comment</label>
        <textarea id="sh-remark" value={remark} onChange={(e) => setRemark(e.target.value)} rows={4} />
        {problem !== "" ? (
          <p className="sh-problem" role="alert">
            {problem}
          </p>
        ) : null}
        <div className="sh-actions">
          <button type="button" disabled={busy || remark.trim() === ""} onClick={() => void send()}>
            Add comment
          </button>
          <button type="button" disabled={busy} onClick={() => void send("request_changes")}>
            Request changes
          </button>
          <button type="button" className="primary" disabled={busy} onClick={() => void send("approve")}>
            Approve
          </button>
        </div>
        {sent.length > 0 ? (
          <section className="sh-sent" aria-label="Sent">
            <h3>Sent to the owner</h3>
            {sent.map((s, i) => (
              // Sent comments only ever append, so their position is their identity.
              // biome-ignore lint/suspicious/noArrayIndexKey: append-only list
              <p key={i}>
                {s.verdict === "approve" ? "Approved. " : s.verdict === "request_changes" ? "Asked for changes. " : ""}
                {s.remark}
              </p>
            ))}
          </section>
        ) : null}
      </aside>
    </div>
  );
}

/** What the page shows for each state of the link; a plain function of its state. */
export function SharedView({
  state,
  onComment,
  onChangeComment = async () => ({ ok: false, reason: "network" }),
}: {
  state: LoadedShare | { status: "loading" };
  onComment: (input: CommentInput) => Promise<SubmitResult>;
  onChangeComment?: (input: ChangeCommentInput) => Promise<SubmitResult>;
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
  if (state.status === "error") {
    return (
      <div className="sh-status">
        <h1>The plan could not be opened</h1>
        <p>{state.message}</p>
      </div>
    );
  }
  return <Ready share={state} onComment={onComment} onChangeComment={onChangeComment} />;
}

/** One link's page; keyed by the id, so another link starts from "loading" again. */
const SharedLink = ({ id }: { id: string }) => {
  const [state, setState] = useState<LoadedShare | { status: "loading" }>({ status: "loading" });

  useEffect(() => {
    let live = true;
    void loadShare(id).then((loaded) => {
      if (live) setState(loaded);
    });
    return () => {
      live = false;
    };
  }, [id]);

  return (
    <SharedView
      state={state}
      onComment={(input) => submitComment(id, input)}
      onChangeComment={(input) => submitChangeComment(id, input)}
    />
  );
};

const Shared = () => {
  const { id = "" } = useParams<{ id?: string }>();
  return (
    <Page className="sh-page">
      <SEO title="A shared plan — QualityLayer" description="A plan shared with you from QualityLayer. Read it and comment on it." />
      <Helmet>
        <meta name="robots" content="noindex" />
      </Helmet>
      <SharedLink key={id} id={id} />
    </Page>
  );
};

export default Shared;
