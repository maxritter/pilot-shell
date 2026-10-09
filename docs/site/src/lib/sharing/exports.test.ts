// @vitest-environment happy-dom
import { afterEach, expect, it, vi } from "vitest";
import { downloadMarkdown, markdownExport } from "./exports";

afterEach(() => vi.restoreAllMocks());
const docs = { "02-plan.md": "# Plan\n\nExact published ütf-8 text.", "agent/private.md": "Private", "../other.md": "Unsafe", "plan-design.png": "Still" };
it("exports exact published text, UTF-8 Markdown and safe filenames only", async () => {
  const file = markdownExport(docs, "02-plan.md");
  expect(file?.name).toBe("02-plan.md");
  expect(await file?.blob.text()).toBe(docs["02-plan.md"]);
  expect(file?.blob.type).toBe("text/markdown;charset=utf-8");
  for (const name of ["agent/private.md", "../other.md", "plan-design.png", "missing.md"]) expect(markdownExport(docs, name)).toBeNull();
});
// Copying is the Reader's Copy menu now; its refusal-then-retry is tested in pages/Shared.dom.test.tsx and pages/SharedDocument.test.tsx.
it("downloads the actual Markdown filename and releases its object URL", () => {
  vi.useFakeTimers();
  const create = vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:published");
  const revoke = vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {});
  const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function () {
    expect(this.download).toBe("02-plan.md"); expect(this.href).toBe("blob:published");
  });
  expect(downloadMarkdown(docs, "02-plan.md")).toBe(true);
  expect(create).toHaveBeenCalledWith(expect.any(Blob));
  expect(click).toHaveBeenCalledOnce();
  vi.advanceTimersByTime(1000);
  expect(revoke).toHaveBeenCalledWith("blob:published");
  vi.useRealTimers();
});
