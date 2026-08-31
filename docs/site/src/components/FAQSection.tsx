import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useInView } from "@/hooks/use-in-view";

const faqItems = [
  {
    question: "How do I add team seats or manage my subscription?",
    answer:
      "Everything is self-service in the customer portal at polar.sh/max-ritter/portal, linked as Manage Subscription in the site header, the footer, and on the pricing page. Sign in with the email you used at checkout and you can change your seat count, switch plans, update your payment method, download invoices, recover your license key, or cancel. Polar also includes a portal link in every order confirmation and renewal email. Seat changes are prorated automatically. Access is always by email sign-in, never by license key: Polar emails a code to the address on the subscription, so only the person who bought it can reach invoices, payment method, seat count, or cancellation. Teammates using a seat have their own license key, and it gives them no way into your billing. Prefer to have it handled for you? Email mail@maxritter.net.",
  },
  {
    question: "Is Pilot Shell enterprise-compliant for data privacy?",
    answer:
      "Pilot Shell's installed local services keep your source code, project files, and development context on your machine. Semble and CodeGraph process code locally, and Pilot disables CodeGraph's optional telemetry. Pilot's required service calls are license validation (license key only) and one-time activation or trial start (machine fingerprint only); they do not include source code, OS information, or version strings. Your overall compliance posture also depends on how your organization configures Claude Code or Codex and its AI provider.",
  },
  {
    question: "Does Pilot Shell send my code or data to external services?",
    answer:
      "Pilot Shell's local services do not upload your source code, project files, prompts, or personal information. Code search (Semble), code intelligence (CodeGraph), persistent memory (Console), session state, and quality hooks run locally; Pilot disables CodeGraph's optional telemetry. Team plans can opt a project into memory sharing, which writes memories into that project's own git repository so teammates receive them — Pilot only writes the files, you review the diff and commit them, and nothing is sent to us. Active AI agents still send the prompts and tool context they need to their provider: Claude Code to Anthropic and Codex to OpenAI. Optional review integrations are disabled by default and send review prompts to their configured provider only when enabled.",
  },
  {
    question: "Does Pilot Shell work with any programming language?",
    answer:
      "Pilot Shell's quality hooks (auto-formatting, linting, type checking) currently support Python, TypeScript/JavaScript, and Go out of the box, plus a single-file dotnet format whitespace check for C#. Pilot workflows, persistent memory, context optimization, and all rules and standards work with any language. You can add custom hooks for additional languages.",
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
          className={`text-center mb-8 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            FAQ
          </h2>
          <p className="text-muted-foreground text-base sm:text-lg mt-3 max-w-3xl mx-auto">
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
