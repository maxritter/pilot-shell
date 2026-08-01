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
    question: "Is Pilot Shell enterprise-compliant for data privacy?",
    answer:
      "Yes. Your source code, project files, and development context never leave your machine through Pilot Shell. The only external calls are license validation (daily, license key only) and one-time activation/trial start (machine fingerprint only). No OS info, no version strings, no analytics, no telemetry. Enterprises using Claude Code with their own API key or Anthropic Enterprise subscription can add Pilot Shell without changing their data compliance posture.",
  },
  {
    question: "Does Pilot Shell send my code or data to external services?",
    answer:
      "Pilot Shell's local services do not upload your source code, project files, prompts, or personal information. Code search (Semble), code intelligence (CodeGraph), persistent memory (Console), session state, and quality hooks run locally, with no analytics, telemetry, or heartbeats. Team plans can opt a project into memory sharing, which writes memories into that project's own git repository so teammates receive them — Pilot only writes the files, you review the diff and commit them, and nothing is sent to us. Active AI agents still send the prompts and tool context they need to their provider: Claude Code to Anthropic, Codex CLI and native Codex review agents to OpenAI. Optional Codex Companion Reviewers also send adversarial review prompts to OpenAI and are disabled by default.",
  },
  {
    question: "Does Pilot Shell work with any programming language?",
    answer:
      "Pilot Shell's quality hooks (auto-formatting, linting, type checking) currently support Python, TypeScript/JavaScript, and Go out of the box, plus a single-file dotnet format whitespace check for C#. TDD enforcement, spec-driven development, persistent memory, context optimization, and all rules and standards work with any language. You can add custom hooks for additional languages.",
  },
  {
    question: "Can I use Pilot Shell on multiple different projects?",
    answer:
      "Yes. Pilot Shell installs once globally and works across all your projects \u2014 you don\u2019t need to reinstall per project. All tools, rules, commands, hooks, and managed review agents live in ~/.pilot/, ~/.claude/, and ~/.codex/ as needed. Just cd into any project and run claude or codex. Each project can optionally have its own .claude/ rules, custom skills, and MCP servers for project-specific behavior. Run /setup-rules in each project to generate project-specific documentation and standards.",
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
