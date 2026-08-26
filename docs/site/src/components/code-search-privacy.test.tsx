import type { ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import FAQSection from "./FAQSection";
import WhatsInside from "./WhatsInside";

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
  it("describes the current local search stack without latency promises", () => {
    const features = renderToStaticMarkup(<WhatsInside />);

    expect(features).toContain("Semble finds code by intent");
    expect(features).toContain("CodeGraph traces runtime structure");
    expect(features).toContain("codegraph_explore");
    expect(features).toContain("read the named source directly");
    expect(features).not.toContain("Sub-300ms");
  });

  it("states the telemetry default and the AI-provider boundary", () => {
    const faq = renderToStaticMarkup(<FAQSection />);

    expect(faq).toContain("Pilot disables CodeGraph&#x27;s optional telemetry");
    expect(faq).toContain("Claude Code to Anthropic and Codex to OpenAI");
    expect(faq).not.toContain("no analytics, no telemetry");
  });
});
