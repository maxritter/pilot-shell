import { ArrowRight, Rocket } from "lucide-react";
import CodeBlock from "@/components/CodeBlock";

const INSTALL_COMMAND =
  "curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash";

const CommandChip = ({ children }: { children: string }) => (
  <code className="ps-chip">{children}</code>
);

const InstallSection = () => (
  <section
    className="ps-sec"
    id="installation"
    aria-labelledby="installation-heading"
    tabIndex={-1}
  >
    <div className="ps-ctr">
      <div className="ps-inst">
        <div className="ps-rv">
          <p className="ps-eyebrow">Getting started</p>
          <h2 className="ps-h2" id="installation-heading">
            Getting Started
          </h2>
          <p className="ps-lead">
            Install once, use everywhere — works with any existing project, no
            matter how complex.
          </p>
          <CodeBlock command={INSTALL_COMMAND} label="install command" wrap />
          <div className="ps-steps-p">
            <Rocket className="h-4 w-4" aria-hidden="true" />
            <p className="ps-sup">
              Open Claude Code. Start with <CommandChip>/setup-rules</CommandChip> —
              it reads your codebase, discovers your conventions, and generates
              project-specific rules. This is how Pilot learns your project. Then
              use <CommandChip>/spec</CommandChip>, <CommandChip>/build</CommandChip>,
              or <CommandChip>/fix</CommandChip> for the work at hand. Pilot Shell
              also supports Codex CLI and Codex in the ChatGPT app.
            </p>
          </div>
          <a className="ps-tlink" href="/docs" style={{ marginTop: 16 }}>
            Read the quick start
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </a>
        </div>

        {/* Demo video — replaces a 2.5MB GIF for ~700KB of MP4/WebM */}
        <div className="ps-vid ps-rv ps-rv-z">
          <video
            width={960}
            height={540}
            poster="/demo-poster.webp"
            controls
            autoPlay
            muted
            loop
            playsInline
            preload="none"
            aria-label="Pilot Shell in action — spec-driven development with Claude Code and Codex"
          >
            <source src="/demo.webm" type="video/webm" />
            <source src="/demo.mp4" type="video/mp4" />
            <track
              kind="captions"
              srcLang="en"
              src="/demo.vtt"
              label="No audio (silent screen recording)"
              default
            />
          </video>
        </div>
      </div>
    </div>
  </section>
);

export default InstallSection;
