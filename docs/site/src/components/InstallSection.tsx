import { Rocket } from "lucide-react";
import { useInView } from "@/hooks/use-in-view";
import CodeBlock from "@/components/CodeBlock";

const INSTALL_COMMAND =
  "curl -fsSL https://raw.githubusercontent.com/maxritter/pilot-shell/main/install.sh | bash";

const CommandChip = ({ children }: { children: string }) => (
  <code className="font-mono text-xs font-medium text-primary bg-primary/10 px-1.5 py-0.5 rounded">
    {children}
  </code>
);

const InstallSection = () => {
  const [ref, inView] = useInView<HTMLDivElement>();

  return (
    <section
      id="installation"
      aria-labelledby="installation-heading"
      className="scroll-mt-24 py-16 lg:py-24 px-4 sm:px-6 relative focus:outline-none"
      tabIndex={-1}
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={ref}
          className={`grid lg:grid-cols-[0.9fr_1.1fr] gap-9 lg:gap-14 items-center ${
            inView ? "animate-fade-in-up" : "opacity-0"
          }`}
        >
          <div className="min-w-0">
            <h2
              id="installation-heading"
              className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground"
            >
              Getting Started
            </h2>
            <p className="text-[15px] leading-relaxed text-muted-foreground mt-3.5">
              Install once, use everywhere — works with any existing project,
              no matter how complex.
            </p>
            <div className="mt-5">
              <CodeBlock command={INSTALL_COMMAND} label="install command" />
            </div>
            <div className="flex items-start gap-3 mt-5">
              <Rocket
                className="h-4 w-4 text-primary flex-none mt-0.5"
                aria-hidden="true"
              />
              <p className="text-[13px] leading-relaxed text-muted-foreground">
                Open Claude Code. Start with <CommandChip>/setup-rules</CommandChip>{" "}
                — it reads your codebase, discovers your conventions, and
                generates project-specific rules. This is how Pilot learns your
                project. Then use <CommandChip>/spec</CommandChip>,{" "}
                <CommandChip>/build</CommandChip>, or{" "}
                <CommandChip>/fix</CommandChip> for the work at hand. Pilot
                Shell also supports Codex CLI and Codex in the ChatGPT app.
              </p>
            </div>
          </div>

          {/* Demo video — replaces a 2.5MB GIF for ~700KB of MP4/WebM */}
          <div
            className="min-w-0 rounded-xl overflow-hidden border border-border/50"
            style={{ aspectRatio: "960 / 540" }}
          >
            <video
              className="w-full h-auto block"
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
};

export default InstallSection;
