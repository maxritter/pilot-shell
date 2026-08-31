import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it, vi } from "vitest";

import Index from "./Index";

vi.mock("@/components/SEO", () => ({ default: () => null }));
vi.mock("@/components/NavBar", () => ({
  default: () => <nav aria-label="Primary" />,
}));
vi.mock("@/components/HeroSection", () => ({
  default: () => <section>Hero</section>,
}));
vi.mock("@/components/AnatomySection", () => ({
  default: () => <section>Anatomy</section>,
}));
vi.mock("@/components/WorkflowSteps", () => ({
  default: () => <section>Workflow</section>,
}));
vi.mock("@/components/SpecCollabSection", () => ({
  default: () => <section>Collaboration</section>,
}));
vi.mock("@/components/TeamSection", () => ({
  default: () => <section>Team</section>,
}));
vi.mock("@/components/InstallSection", () => ({
  default: () => <section>Install</section>,
}));
vi.mock("@/components/ConsoleSection", () => ({
  default: () => <section>Console</section>,
}));
vi.mock("@/components/AgentsSection", () => ({
  default: () => <section>Agents</section>,
}));
vi.mock("@/components/TestimonialsSection", () => ({
  default: () => <section>Testimonials</section>,
}));
vi.mock("@/components/FAQSection", () => ({
  default: () => <section>FAQ</section>,
}));
vi.mock("@/components/Footer", () => ({
  default: () => <footer>Footer</footer>,
}));

async function renderIndexPage(): Promise<string> {
  const stream = await renderToReadableStream(
    <Index />,
  );

  await stream.allReady;
  return new Response(stream).text();
}

describe("homepage landmarks", () => {
  it("renders the global footer outside the main landmark", async () => {
    const markup = await renderIndexPage();
    const mainStart = markup.indexOf("<main");
    const mainEnd = markup.indexOf("</main>");
    const footerStart = markup.indexOf("<footer");

    expect(mainStart).toBeGreaterThanOrEqual(0);
    expect(mainEnd).toBeGreaterThan(mainStart);
    expect(footerStart).toBeGreaterThan(mainEnd);
    expect(markup.slice(mainStart, mainEnd)).not.toContain("<footer");
  });
});
