import { HelpCircle } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useInView } from "@/hooks/use-in-view";

const faqItems = [
  {
    question: "Does Pilot Shell send my code or data to external services?",
    answer:
      "No code, files, prompts, project data, or personal information ever leaves your machine through Pilot Shell. All development tools \u2014 vector search, persistent memory, session state, and quality hooks \u2014 run entirely locally. Pilot Shell makes exactly three external calls, all for licensing only: (1) License validation \u2014 once every 24 hours, sends your license key and organization ID to api.polar.sh. (2) License activation \u2014 one-time, sends license key and a machine fingerprint to api.polar.sh. (3) Trial start \u2014 one-time, sends a hashed hardware fingerprint to pilot-shell.com to generate a 7-day trial key. That\u2019s the complete list. No OS info, no version strings, no analytics, no telemetry, no heartbeats. The validation result is cached locally, and Pilot Shell works fully offline for up to 7 days.",
  },
  {
    question: "Is Pilot Shell enterprise-compliant for data privacy?",
    answer:
      "Yes. Your source code, project files, and development context never leave your machine through Pilot Shell. The only external calls are license validation (daily, license key only) and one-time activation/trial start (machine fingerprint only). No OS info, no version strings, no analytics, no telemetry. Enterprises using Claude Code with their own API key or Anthropic Enterprise subscription can add Pilot Shell without changing their data compliance posture.",
  },
  {
    question: "What are the licenses of Pilot Shell's dependencies?",
    answer:
      "All external tools and dependencies that Pilot Shell installs and uses are open source. This includes ruff, basedpyright, Prettier, ESLint, gofmt, uv, Probe, agent-browser, and all MCP servers. Most are permissive (MIT, Apache 2.0, BSD). hypothesis uses MPL-2.0 (weak copyleft, test-only) — no GPL or AGPL dependencies are introduced into your environment.",
  },
  {
    question: "Do I need a separate Anthropic subscription?",
    answer:
      "Yes. Pilot Shell enhances Claude Code \u2014 it doesn't replace it. You need an active Claude subscription \u2014 Max 5x or 20x for solo developers, or Team Premium for teams and companies. Using the Anthropic API directly is also possible but may lead to much higher costs. Pilot Shell adds quality automation on top of whatever Claude Code access you already have.",
  },
  {
    question:
      "Does Pilot Shell work with Codex, Gemini CLI, OpenCode, or other AI coding tools?",
    answer:
      "No. Pilot Shell is built exclusively for Claude Code. Every hook, rule, command, and workflow is engineered specifically for Claude\u2019s tool-use protocol, prompt format, and session lifecycle. Pilot Shell also only supports Claude Sonnet 4.6 and Claude Opus 4.6 \u2014 these are the models that produce the best results, and every rule and prompt is optimized for their behavior. Supporting other tools or models would mean compromising on quality, which is the opposite of what Pilot Shell is designed to do.",
  },
  {
    question: "Does Pilot Shell work with existing projects?",
    answer:
      "Yes \u2014 that's the primary use case. Pilot Shell doesn't scaffold or restructure your code. You install it, run /setup-rules, and it explores your codebase to discover your tech stack, conventions, and patterns. From there, every session has full context about your project. The more complex and established your codebase, the more value Pilot Shell adds \u2014 quality hooks catch regressions, persistent memory preserves decisions across sessions, and /spec plans features against your real architecture.",
  },
  {
    question: "Does Pilot Shell work with any programming language?",
    answer:
      "Pilot Shell's quality hooks (auto-formatting, linting, type checking) currently support Python, TypeScript/JavaScript, and Go out of the box. TDD enforcement, spec-driven development, persistent memory, context optimization, and all rules and standards work with any language that Claude Code supports. You can add custom hooks for additional languages.",
  },
  {
    question: "Can I use one license on multiple machines?",
    answer:
      "Yes. A Solo license covers you across all your personal devices \u2014 workstation, laptop, VPS, cloud instances. One subscription, one key, multiple machines. No need for a Team plan just because you work from more than one device. Team licenses are for multiple people, not multiple machines.",
  },
  {
    question: "Can I use Pilot Shell on multiple projects?",
    answer:
      "Yes. Pilot Shell installs once globally and works across all your projects \u2014 you don\u2019t need to reinstall per project. All tools, rules, commands, and hooks live in ~/.pilot/ and ~/.claude/, available everywhere. Just cd into any project and run pilot. Each project can optionally have its own .claude/ rules, custom skills, and MCP servers for project-specific behavior. Run /setup-rules in each project to generate project-specific documentation and standards.",
  },
  {
    question: "Do I need to run the installer from inside a project directory?",
    answer:
      "No. You can run the installer from any directory \u2014 your home folder, a parent folder containing multiple repos, anywhere. Everything installs globally to ~/.pilot/ and ~/.claude/.",
  },
  {
    question:
      "Should I still use Claude Code's built-in plan mode (Shift+Tab)?",
    answer:
      "No \u2014 use /spec instead. Claude Code\u2019s built-in plan mode is unstructured: plans live only in the conversation, have no consistent format, aren\u2019t saved as files, and disappear when the session ends. There\u2019s no verification, no TDD enforcement, and no way to resume or review a plan later. /spec is a drop-in replacement that fixes all of this. Plans are written as structured markdown files in docs/plans/ with a consistent format \u2014 scope, tasks, definition of done, and approval status. They persist across sessions, can be edited before approval, and drive a complete workflow: plan \u2192 implement with TDD \u2192 verify with code review. Use /spec for all planned work. Use Quick Mode (regular chat) for small tasks and exploration.",
  },
  {
    question:
      "Why does Pilot Shell use bypass permissions mode by default?",
    answer:
      "Pilot Shell sets Claude Code to bypassPermissions mode so the /spec workflow can run autonomously \u2014 planning, implementing, and verifying without pausing for permission prompts at every tool call. In Quick Mode (regular chat), you have full control: press Shift+Tab at any time to cycle through Claude Code\u2019s permission modes \u2014 Plan mode (propose then approve), Accept Edits (auto-approve file changes), or Normal mode (fine-grained prompts for each action). You can also set a persistent default in ~/.claude/settings.json by changing the defaultMode field. Pilot Shell preserves your choice across updates \u2014 the installer merges permissions additively and never overwrites your customizations.",
  },
  {
    question: "Can I add my own rules, commands, skills, and agents?",
    answer:
      "Yes. Create your own in your project\u2019s .claude/ folder \u2014 rules, commands, skills, and agents are all plain markdown files. Your project-level assets load alongside Pilot Shell\u2019s built-in defaults and take precedence when they overlap. /setup-rules auto-discovers your codebase patterns and generates project-specific rules. /create-skill builds reusable skills from any topic interactively. View and manage all extensions on the Console Extensions page. Team plan users can also share extensions via a connected git repository \u2014 push, pull, and compare versions with your team.",
  },
  {
    question: "Can I control Pilot Shell from my phone?",
    answer:
      "Yes \u2014 using Claude Code\u2019s Remote Control feature. Start a session via pilot on your computer, then type /remote-control to make it accessible from the Claude Mobile App (iOS/Android) under the Code tab. You can also enable it globally via /config \u2192 \u201cEnable Remote Control for all sessions\u201d. Remote Control requires the native install of Claude Code (curl -fsSL https://claude.ai/install.sh | bash), not the npm version. Your computer must stay awake \u2014 on macOS, use Amphetamine to keep your Mac awake with the display off. To start sessions directly from your phone, install Termius on your mobile device, SSH into your computer, and run pilot. For SSH access outside your home network, install Tailscale on both devices \u2014 the Claude App approach works everywhere without extra setup. If Remote Control doesn\u2019t connect, run /logout followed by /login inside Claude Code to re-authenticate.",
  },
  {
    question: "Can I use Pilot Shell inside a Dev Container?",
    answer:
      "Yes. Copy the .devcontainer folder from the Pilot Shell repository into your project, adapt it to your needs (base image, extensions, dependencies), and install Pilot Shell inside the container. Everything works the same \u2014 hooks, rules, MCP servers, persistent memory, and the Console dashboard all run inside the container. This is a great option for teams that want a consistent, reproducible development environment.",
  },
];

const FAQSection = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [contentRef, contentInView] = useInView<HTMLDivElement>();

  return (
    <section id="faq" className="py-16 lg:py-24 px-4 sm:px-6 relative">
      <div className="max-w-3xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div
          ref={headerRef}
          className={`text-center mb-12 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
              <HelpCircle className="h-5 w-5 text-primary" />
            </div>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            FAQ
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            Common questions about Pilot Shell, data privacy, and compatibility.
          </p>
        </div>

        <div
          ref={contentRef}
          className={`rounded-lg border border-border/50 bg-card overflow-hidden ${contentInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <Accordion type="single" collapsible className="px-6">
            {faqItems.map((item, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="border-border/50"
              >
                <AccordionTrigger className="text-left text-foreground hover:text-primary hover:no-underline text-sm sm:text-base py-5">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground text-sm leading-relaxed">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  );
};

export default FAQSection;
