/**
 * What a link reviewer has written and not sent: answers to the owner's questions, and comments.
 * Everything leaves together, when they choose Send. Pure, so the page's state is testable.
 */

import { answerWords, type GuestAnswer, type Remark, type ShareItem } from "./sharing";

export type Drafts = {
  /** By question id. A change or a reply counts once it says something. */
  answers: Record<string, { answer: GuestAnswer; note: string }>;
  /** Comments on a passage, on a point of the change, or replies on a thread the guest started. */
  remarks: Exclude<Remark, { kind: "item" }>[];
};

export const EMPTY: Drafts = { answers: {}, remarks: [] };

/** Pick an answer for a question, or take it back with `null`. The note is what they wrote beside it. */
export function answerItem(drafts: Drafts, id: string, answer: GuestAnswer | null, note = ""): Drafts {
  const { [id]: _taken, ...rest } = drafts.answers;
  return { ...drafts, answers: answer === null ? rest : { ...rest, [id]: { answer, note } } };
}

/** Add a comment; one with no words is not one. */
export function addRemark(drafts: Drafts, remark: Drafts["remarks"][number]): Drafts {
  if (remark.text.trim() === "") return drafts;
  return { ...drafts, remarks: [...drafts.remarks, { ...remark, text: remark.text.trim() }] };
}

export function removeRemark(drafts: Drafts, index: number): Drafts {
  return { ...drafts, remarks: drafts.remarks.filter((_, i) => i !== index) };
}

const complete = (a: { answer: GuestAnswer; note: string }) => a.answer === "agree" || a.note.trim() !== "";

/** What would leave now: the answers in the order the owner asked, then the comments. */
export function pending(drafts: Drafts, items: readonly ShareItem[]): Remark[] {
  const answers = items.flatMap((item): Remark[] => {
    const a = drafts.answers[item.id];
    if (a === undefined || !complete(a)) return [];
    return [{ kind: "item", id: item.id, step: item.step, what: item.what, answer: a.answer, label: answerWords(item, a.answer), note: a.note.trim() }];
  });
  return [...answers, ...drafts.remarks];
}

/** "1 of 3 answered · 2 comments". */
export function summary(drafts: Drafts, items: readonly ShareItem[]): { answered: number; total: number; comments: number } {
  const answered = items.filter((item) => {
    const a = drafts.answers[item.id];
    return a !== undefined && complete(a);
  }).length;
  return { answered, total: items.length, comments: drafts.remarks.length };
}
