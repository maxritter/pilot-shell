import type { ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import AnatomySection from "./AnatomySection";
import FAQSection from "./FAQSection";

interface ChildrenProps {
  children: ReactNode;
}

vi.mock("@/components/ui/accordion", () => ({
  Accordion: ({ children }: ChildrenProps) => <div>{children}</div>,
  AccordionContent: ({ children }: ChildrenProps) => <div>{children}</div>,
  AccordionItem: ({ children }: ChildrenProps) => <div>{children}</div>,
  AccordionTrigger: ({ children }: ChildrenProps) => <div>{children}</div>,
}));

describe("code search and privacy copy", () => {
  it("grounds context engineering in the local search stack", () => {
    const anatomy = renderToStaticMarkup(<AnatomySection />);

    expect(anatomy).toContain("Semble");
    expect(anatomy).toContain("CodeGraph");
    expect(anatomy).toContain("reads the named source instead");
    expect(anatomy).not.toContain("Sub-300ms");
  });

  it("states the telemetry default and the AI-provider boundary", () => {
    const faq = renderToStaticMarkup(<FAQSection />);

    expect(faq).toContain("Pilot disables CodeGraph&#x27;s optional telemetry");
    expect(faq).toContain("Claude Code to Anthropic and Codex to OpenAI");
    expect(faq).not.toContain("no analytics, no telemetry");
  });
});
