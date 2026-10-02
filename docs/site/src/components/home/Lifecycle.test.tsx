import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it } from "vitest";
import { OPTIONAL_STEPS } from "@ql/core/optional-steps.ts";
import { ROUTE_LIST } from "@ql/core/task/route-picture.ts";
import { DemoTourProvider } from "./demoTour";
import Lifecycle from "./Lifecycle";

async function render(): Promise<string> {
  const stream = await renderToReadableStream(
    <DemoTourProvider>
      <Lifecycle />
    </DemoTourProvider>,
  );
  await stream.allReady;
  return new Response(stream).text();
}

describe("the lifecycle", () => {
  it("has a tab for every route the product offers and names every optional step", async () => {
    const html = await render();
    const tabs = html.match(/class="w7-seg-b[^"]*"/g) ?? [];
    expect(tabs).toHaveLength(ROUTE_LIST.length);
    for (const step of OPTIONAL_STEPS) expect(html).toContain(`>${step.label}</`);
  });
});
