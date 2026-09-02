import { Fragment } from "react";
import { BookOpen, Bell, ChevronRight, Github } from "lucide-react";
import CodeBlock from "@/components/CodeBlock";

const INSTALL_COMMAND =
  "curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash";

/** The headline reveals word by word; each word carries its own delay class. */
const HEADLINE = ["From", "requirement", "to", "production-grade", "code", "—"];
const HEADLINE_ACCENT = ["planned,", "tested,", "verified."];

const Word = ({ index, children }: { index: number; children: string }) => (
  <span className={`ps-w ps-w${index}`}>{children}</span>
);

/* A terminal stays dark in both site themes — the palette lives in site.css. */
const TerminalMock = () => (
  <div className="ps-term" aria-hidden="true">
    <div className="ps-term-bar">
      <div className="ps-dots">
        <span style={{ background: "hsl(0 60% 55%)" }} />
        <span style={{ background: "hsl(40 80% 55%)" }} />
        <span style={{ background: "hsl(140 50% 45%)" }} />
      </div>
      <span className="ps-term-title">claude — api-service</span>
      <span className="ps-t-faint">80×24</span>
    </div>
    <div className="ps-term-body">
      <div className="ps-tl">
        <span className="ps-g ps-t-blue">&gt;</span>
        <span className="ps-t-fg">
          <span className="ps-t-cmd">/spec add rate limiting to the public API</span>
          <span className="ps-caret" />
        </span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-faint">⋯</span>
        <span>
          exploring codebase{" "}
          <span className="ps-t-faint">— Semble ×6 · CodeGraph ×2 · 3 memories recalled</span>
        </span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-green">✓</span>
        <span className="ps-t-fg">
          plan written — 4 tasks <span className="ps-t-faint">· approved by you</span>
        </span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-red">✗</span>
        <span>
          <span className="ps-t-red">RED</span> test_rate_limit_returns_429{" "}
          <span className="ps-t-faint">· fails, as expected</span>
        </span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-green">✓</span>
        <span>
          <span className="ps-t-green">GREEN</span>{" "}
          <span className="ps-t-faint">· ruff · basedpyright · 218 tests passed</span>
        </span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-amber">■</span>
        <span className="ps-t-amber">
          stop guard <span className="ps-t-fg">— completion blocked, E2E evidence missing</span>
        </span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-green">✓</span>
        <span className="ps-t-fg">verified in browser — evidence saved to Console</span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-blue">&gt;</span>
        <span className="ps-cur" />
      </div>
    </div>
    <div className="ps-term-foot">
      <span>
        <span className="ps-t-blue">Pilot Shell</span> · opusplan · ctx 34% · git:main
      </span>
    </div>
  </div>
);

const HeroSection = () => (
  <section className="ps-hero" id="hero" aria-labelledby="hero-heading">
    <div className="ps-ctr ps-hero-stack">
      <a className="ps-pill ps-e ps-e1" href="#anatomy">
        <span className="ps-pill-tag">Harness</span>
        <span>How real engineers run Claude Code and Codex</span>
        <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
      </a>

      <h1 className="ps-h1" id="hero-heading">
        {HEADLINE.map((word, i) => (
          <Fragment key={word}>
            <Word index={i + 1}>{word}</Word>{" "}
          </Fragment>
        ))}
        <span className="ps-brand-txt">
          {HEADLINE_ACCENT.map((word, i) => (
            <Fragment key={word}>
              <Word index={HEADLINE.length + i + 1}>{word}</Word>
              {i < HEADLINE_ACCENT.length - 1 ? " " : null}
            </Fragment>
          ))}
        </span>
      </h1>

      <p className="ps-hero-lead ps-e ps-e3">
        Pilot Shell is a professional context and harness engineering system for
        Claude Code and Codex. It coordinates the complete engineering process
        around the model — with quality enforced on every layer.
      </p>

      <div className="ps-cta-row ps-e ps-e4">
        <a
          className="ps-btn ps-btn-pri"
          href="https://github.com/maxritter/pilot-shell"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Github className="h-4 w-4" aria-hidden="true" />
          View on GitHub
        </a>
        <a className="ps-btn ps-btn-out" href="/docs">
          <BookOpen className="h-4 w-4" aria-hidden="true" />
          Docs
        </a>
      </div>

      <div className="ps-install ps-e ps-e5">
        <CodeBlock command={INSTALL_COMMAND} label="install command" />
        <p className="ps-sup ps-hero-note">
          macOS · Linux · Windows (WSL2) — installs in under 2 minutes. Works
          with any existing project.
        </p>
      </div>

      <div className="ps-mock-wrap ps-e ps-e6">
        <TerminalMock />
        <div className="ps-toast" role="status">
          <span className="ps-tile">
            <Bell className="h-[18px] w-[18px]" aria-hidden="true" />
          </span>
          <div>
            <div className="ps-toast-t">Verification complete</div>
            <div className="ps-toast-s">evidence saved — Console · localhost:41777</div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

export default HeroSection;
