import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it } from "vitest";
import { embedUrl, FILMS } from "@/lib/films";
import Films from "./Films";

async function render(): Promise<string> {
  const stream = await renderToReadableStream(<Films />);
  await stream.allReady;
  return new Response(stream).text();
}

describe("the videos section", () => {
  it("shows both films as local posters and loads nothing from YouTube before play", async () => {
    const html = await render();
    expect(html).toContain('id="videos"');
    for (const film of FILMS) {
      expect(html).toContain(`src="${film.poster}"`);
      expect(html).toContain(`aria-label="Play the QualityLayer ${film.name.toLowerCase()} video, ${film.length}"`);
    }
    expect(html).not.toContain("<iframe");
    expect(html).not.toMatch(/youtube(-nocookie)?\.com/);
  });

  it("plays through the privacy-enhanced player", () => {
    expect(embedUrl("FQuSwPxdNzk")).toBe("https://www.youtube-nocookie.com/embed/FQuSwPxdNzk?autoplay=1&rel=0");
  });
});
