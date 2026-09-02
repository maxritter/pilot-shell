import { useState } from "react";
import { ChevronDown, CircleHelp } from "lucide-react";

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
      "Yes. Pilot Shell installs once globally and works across all your projects — you don’t need to reinstall per project. All tools, rules, commands, hooks, and managed review agents live in ~/.pilot/, ~/.claude/, and ~/.codex/ as needed. Just cd into any project and run claude or codex. Each project can optionally have its own .claude/ rules, custom skills, and MCP servers for project-specific behavior. Run /setup-rules in each project to generate project-specific documentation and standards.",
  },
  {
    question: "Can I use Pilot Shell inside a Dev Container?",
    answer:
      "Yes. Copy the .devcontainer folder from the Pilot Shell repository into your project, adapt it to your needs (base image, extensions, dependencies), and install Pilot Shell inside the container. Everything works the same — hooks, rules, MCP servers, persistent memory, and the Console dashboard all run inside the container. This is a great option for teams that want a consistent, reproducible development environment.",
  },
];

const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState(-1);

  return (
    <section className="ps-sec" id="faq" aria-labelledby="faq-heading">
      <div className="ps-ctr">
        <div className="ps-sec-hd ps-left ps-rv">
          <h2 className="ps-h2" id="faq-heading">
            FAQ
          </h2>
          <p className="ps-lead">
            Common questions about Pilot Shell, data privacy, and compatibility.
          </p>
        </div>

        <div className="ps-faqbox ps-stg">
          {faqItems.map((item, index) => {
            const isOpen = openIndex === index;
            return (
              <div key={item.question} className={`ps-fitem${isOpen ? " ps-open" : ""}`}>
                <h3 className="ps-h4" style={{ fontSize: "inherit" }}>
                  <button
                    type="button"
                    className="ps-fq"
                    aria-expanded={isOpen}
                    aria-controls={`faq-body-${index}`}
                    onClick={() => setOpenIndex(isOpen ? -1 : index)}
                  >
                    <CircleHelp className="h-[18px] w-[18px] ps-qi" aria-hidden="true" />
                    <span className="ps-fq-t">{item.question}</span>
                    <ChevronDown className="h-[18px] w-[18px] ps-chev" aria-hidden="true" />
                  </button>
                </h3>
                <div className="ps-fa-body" id={`faq-body-${index}`}>
                  <div className="ps-fa-in">
                    <p className="ps-fa-txt">{item.answer}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FAQSection;
