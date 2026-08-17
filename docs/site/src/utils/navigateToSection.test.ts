import { afterEach, describe, expect, it, vi } from "vitest";

import { navigateToSection } from "./navigateToSection";

describe("navigateToSection", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("scrolls to and focuses the resolved section", () => {
    const target = {
      focus: vi.fn(),
      hasAttribute: vi.fn(() => false),
      scrollIntoView: vi.fn(),
      setAttribute: vi.fn(),
    };
    const querySelector = vi.fn(() => target);
    vi.stubGlobal("CSS", { escape: (value: string) => value });
    vi.stubGlobal("document", { querySelector });
    vi.stubGlobal("window", {
      matchMedia: vi.fn(() => ({ matches: false })),
    });
    const navigate = vi.fn();

    navigateToSection("#installation", "/", navigate);

    expect(querySelector).toHaveBeenCalledWith("#installation");
    expect(target.scrollIntoView).toHaveBeenCalledWith({ behavior: "smooth" });
    expect(target.setAttribute).toHaveBeenCalledWith("tabindex", "-1");
    expect(target.focus).toHaveBeenCalledWith({ preventScroll: true });
    expect(navigate).not.toHaveBeenCalled();
  });

  it("uses instant scrolling when reduced motion is requested", () => {
    const target = {
      focus: vi.fn(),
      hasAttribute: vi.fn(() => true),
      scrollIntoView: vi.fn(),
      setAttribute: vi.fn(),
    };
    vi.stubGlobal("CSS", { escape: (value: string) => value });
    vi.stubGlobal("document", { querySelector: vi.fn(() => target) });
    vi.stubGlobal("window", {
      matchMedia: vi.fn(() => ({ matches: true })),
    });

    navigateToSection("installation", "/", vi.fn());

    expect(target.scrollIntoView).toHaveBeenCalledWith({ behavior: "auto" });
  });
});
