import type { Drafts } from "@/lib/sharing/drafts";
import { mockupHtml } from "@/lib/sharing/plan";
import { answerWords, type GuestAnswer, type ItemMedia, type ShareItem } from "@/lib/sharing/sharing";
import { Diagram } from "./Diagram";
import { MissingMockup, MockupFrame } from "./Frame";


/**
 * The questions the owner asks, as the App shows them under Needs you: the kind, what is asked,
 * the thing itself (a mockup, a diagram) and the answers of its family. Answers stay in the page
 * until the reviewer sends them with their comments.
 */

function Media({ media, docs }: { media: ItemMedia; docs: Record<string, string> }) {
  if (media.kind === "artifact") {
    const html = mockupHtml(docs, media.name);
    return html === undefined ? <MissingMockup /> : <MockupFrame html={html} title={media.title ?? "Mockup"} />;
  }
  if (media.kind === "mermaid") return <Diagram source={media.source} title={media.title} />;
  return <p className="sh-ask-text">{media.text}</p>;
}

const NOTE_LABEL: Record<Exclude<GuestAnswer, "agree">, string> = { change: "What should change?", reply: "Your reply" };

function Ask({
  item,
  docs,
  draft,
  sentAs,
  onAnswer,
}: {
  item: ShareItem;
  docs: Record<string, string>;
  draft: Drafts["answers"][string] | undefined;
  sentAs: string | undefined;
  onAnswer: (id: string, answer: GuestAnswer | null, note?: string) => void;
}) {
  const noteId = `sh-note-${item.id}`;
  return (
    <li className={sentAs !== undefined ? "sh-ask settled" : "sh-ask"} data-testid="shared-ask">
      <span className={sentAs !== undefined ? "sh-mark done" : "sh-mark you"} aria-hidden="true" />
      <div className="sh-ask-head">
        <div className="sh-kind">{item.kindLabel}</div>
        <div className="sh-what">{item.what}</div>
        {item.why !== undefined ? <div className="sh-why">{item.why}</div> : null}
        {item.members !== undefined ? (
          <ul className="sh-members">
            {item.members.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        ) : null}
      </div>
      {sentAs !== undefined ? (
        <div className="sh-acts sh-sentas">{`You answered: ${sentAs}. Sent.`}</div>
      ) : (
        <div className="sh-acts" role="group" aria-label={`Your answer: ${item.what}`}>
          {item.options.map((option) => (
            <button
              key={option}
              type="button"
              className={option === item.options[0] ? "sh-btn sm" : "sh-btn sm quiet"}
              aria-pressed={draft?.answer === option}
              onClick={() => onAnswer(item.id, draft?.answer === option ? null : option, draft?.answer === option ? "" : (draft?.note ?? ""))}
            >
              {answerWords(item, option)}
            </button>
          ))}
        </div>
      )}
      {sentAs === undefined && draft !== undefined && draft.answer !== "agree" ? (
        <div className="sh-ask-full sh-ask-note">
          <label htmlFor={noteId}>{NOTE_LABEL[draft.answer]}</label>
          <textarea id={noteId} rows={2} value={draft.note} onChange={(e) => onAnswer(item.id, draft.answer, e.target.value)} />
        </div>
      ) : null}
      {item.media !== undefined ? (
        <div className="sh-ask-full">
          <Media media={item.media} docs={docs} />
        </div>
      ) : null}
    </li>
  );
}

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

export function Asks({
  items,
  owner,
  docs,
  drafts,
  settled,
  onAnswer,
}: {
  items: ShareItem[];
  owner: string | undefined;
  docs: Record<string, string>;
  drafts: Drafts;
  /** Questions already sent, by id, with the words of the answer. */
  settled: Record<string, string>;
  onAnswer: (id: string, answer: GuestAnswer | null, note?: string) => void;
}) {
  if (items.length === 0) return null;
  return (
    <section className="sh-asks" aria-label={`${owner ?? "The owner"} asks you`}>
      <header className="sh-asks-head">
        <span className="sh-mark you" aria-hidden="true" />
        <h2>{`${owner ?? "The owner"} asks you`}</h2>
        <span className="sh-asks-side">
          {`${plural(items.length, "question", "questions")} · your answers reach ${owner ?? "the owner"} as comments`}
        </span>
      </header>
      <ul>
        {items.map((item) => (
          <Ask key={item.id} item={item} docs={docs} draft={drafts.answers[item.id]} sentAs={settled[item.id]} onAnswer={onAnswer} />
        ))}
      </ul>
    </section>
  );
}
