import { readFileSync } from "node:fs";
import { Window } from "happy-dom";
import { describe, expect, it } from "vitest";

const palette = readFileSync(new URL("../../../../qualitylayer/src/ui/brand/palette.css", import.meta.url), "utf8");
const css = readFileSync(new URL("../../../docusaurus/src/css/custom.css", import.meta.url), "utf8").replace(/^@import.*$/gm, "");
const luminance = (hex: string) => {
  const values = hex.slice(1).match(/../g)!.map((channel) => {
    const s = parseInt(channel, 16) / 255;
    return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return values[0] * 0.2126 + values[1] * 0.7152 + values[2] * 0.0722;
};

describe("documentation footer contrast", () => {
  for (const theme of ["light", "dark"]) {
    it(`keeps the headings readable on the dark footer in ${theme} mode`, async () => {
      const window = new Window();
      window.document.documentElement.dataset.theme = theme;
      const style = window.document.createElement("style");
      style.textContent = `${palette}\n${css}`;
      window.document.head.append(style);
      // The footer's own foreground and surface, as supplied by Docusaurus's dark footer.
      window.document.body.innerHTML = '<footer class="footer footer--dark" style="color: #ebedf0; background-color: #303846"><h3 class="footer__title">Docs</h3></footer>';
      const title = window.document.querySelector("h3")!;
      const foreground = window.getComputedStyle(title).color;
      const background = window.getComputedStyle(title.parentElement!).backgroundColor;
      const a = luminance(foreground), b = luminance(background);
      expect((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toBeGreaterThanOrEqual(4.5);
      await window.happyDOM.close();
    });
  }
});
