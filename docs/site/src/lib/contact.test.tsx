import { describe, expect, it } from "vitest";
import { render } from "../prerender";
import { LEGAL_PATHS } from "./legal";
import { CONTACT_EMAIL } from "./product";

describe("public contact destinations", () => {
  it("keeps the approved product mailbox independent of the author's personal address", () => {
    expect(CONTACT_EMAIL).toBe("hello@qualitylayer.dev");
  });

  it.each(["/", "/pricing", "/download", "/compare", ...LEGAL_PATHS])(
    "%s sends every public email link to the product mailbox",
    async (path) => {
      const { body } = await render(path);
      const destinations = [...body.matchAll(/href="mailto:([^"?]+)(?:\?[^"]*)?"/g)].map((match) => match[1]);
      expect(destinations.length).toBeGreaterThan(0);
      expect(new Set(destinations)).toEqual(new Set(["hello@qualitylayer.dev"]));
      if (path === "/pricing") {
        expect(body).toMatch(/href="mailto:hello@qualitylayer\.dev\?subject=QualityLayer%20Enterprise"[^>]*>Contact us<\/a>/);
      }
    },
  );
});
