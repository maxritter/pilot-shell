import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import { COMPARISONS, ROUNDUP_FAQS, ROUNDUP_PATH, type Comparison, type ComparisonSource } from "@/lib/comparisons";
import { SITE_URL } from "@/lib/product";
import { pageMetadata } from "@/lib/seo";
import { faqStructuredData } from "@/lib/structured-data";
import "@/styles/comparisons.css";

function Sources({ sources }: { sources: ComparisonSource[] }) {
  return (
    <section className="cp-sources" aria-labelledby="sources">
      <h2 id="sources">Sources, checked October 2026</h2>
      <p>Checked on <time dateTime="2026-10-19">October 19, 2026</time>. This is QualityLayer's comparison of public documentation, not a hands-on benchmark.</p>
      <ol>
        {sources.map(({ label, url }, index) => <li key={url} id={`source-${index + 1}`}><a href={url}>{label}</a></li>)}
      </ol>
      <p>QualityLayer's claims follow its <a href="/docs/steps/plan">Plan</a>, <a href="/docs/steps/verify">Verify</a>, <a href="/docs/steps/review">Review</a> and <a href="/docs/steps/pull-request">pull request</a> guides. Availability and behavior can change; check the linked docs for your setup.</p>
    </section>
  );
}

function ComparisonLinks({ current }: { current?: string }) {
  return (
    <ul className="cp-links">
      {COMPARISONS.filter(({ slug }) => slug !== current).map(({ slug, name, summary }) => (
        <li key={slug}>
          <Link to={`/compare/${slug}`}>QualityLayer vs {name}</Link>
          <p>{summary}</p>
        </li>
      ))}
    </ul>
  );
}

function ProofAndReview() {
  return (
    <section aria-labelledby="proof">
      <h2 id="proof">How QualityLayer carries proof into review</h2>
      <p>The <a href="/docs/steps/verify">Verify step</a> records output, screenshots or files for each agreed outcome. Checks that fail or cannot run stay visible in <a href="/docs/steps/review">Review</a>.</p>
      <p>Independent review depends on risk and settings. On a change that is not risky, the build session can review its own work and marks that review <em>not independent</em>.</p>
      <p>You approve the Plan before implementation and the result at Review. With GitHub's <code>gh</code> CLI, QualityLayer <a href="/docs/steps/pull-request">follows the pull request</a> through checks and review until you merge it. QualityLayer never merges it.</p>
    </section>
  );
}

function Frame({ title, lead, sources, children, faq = false }: {
  title: string;
  lead: string;
  sources: ComparisonSource[];
  children: ReactNode;
  faq?: boolean;
}) {
  const { pathname } = useLocation();
  const metadata = pageMetadata(pathname);
  const breadcrumbs = [{ name: "Home", path: "/" }, { name: "Compare", path: "/compare" }];
  if (pathname !== "/compare") breadcrumbs.push({ name: title, path: pathname });
  const structuredData = [
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "@id": `${metadata.canonicalUrl}#webpage`,
      url: metadata.canonicalUrl,
      name: metadata.title,
      description: metadata.description,
      inLanguage: "en",
      lastReviewed: "2026-10-19",
      publisher: { "@type": "Organization", name: "QualityLayer", url: SITE_URL },
      citation: sources.map(({ url }) => url),
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: breadcrumbs.map(({ name, path }, index) => ({
        "@type": "ListItem", position: index + 1, name, item: `${SITE_URL}${path}`,
      })),
    },
    ...(faq ? [faqStructuredData(ROUNDUP_FAQS)] : []),
  ];
  return (
    <>
      <SEO structuredData={structuredData} />
      <Page className="cp-page">
        <article className="w7-wrap cp-article">
          <nav aria-label="Breadcrumb" className="cp-breadcrumb">
            <ol>{breadcrumbs.map(({ name, path }, index) => <li key={path}>{index === breadcrumbs.length - 1 ? <span aria-current="page">{name}</span> : <Link to={path}>{name}</Link>}</li>)}</ol>
          </nav>
          <header className="cp-header">
            <h1>{title}</h1>
            <p className="w7-lead">{lead}</p>
          </header>
          {children}
          <Sources sources={sources} />
        </article>
      </Page>
    </>
  );
}

function HeadToHead({ comparison: c }: { comparison: Comparison }) {
  return (
    <Frame title={`QualityLayer vs ${c.name}`} lead={c.lead} sources={c.sources}>
      <section aria-labelledby="strengths">
        <h2 id="strengths">Where {c.name} is strong</h2>
        <p>{c.strengths} <a href="#source-1">[1]</a>{c.slug === "kiro" && <> <a href="#source-2">[2]</a></>}</p>
      </section>
      <section aria-labelledby="agents">
        <h2 id="agents">Working with Claude Code and Codex</h2>
        <p>{c.agents} <a href={`#source-${c.sources.length}`}>[{c.sources.length}]</a>{c.slug === "humanlayer" && <> <a href="#source-1">[1]</a></>}</p>
      </section>
      <section aria-labelledby="workflow">
        <h2 id="workflow">Compare the workflow</h2>
        <div className="cp-table-scroll" role="region" aria-label={`${c.name} and QualityLayer workflow table`} tabIndex={0}>
          <table>
            <caption>Documented approaches to planning and checking a change</caption>
            <thead><tr><th scope="col">Your task</th><th scope="col">QualityLayer</th><th scope="col">{c.name}</th></tr></thead>
            <tbody>{c.rows.map(({ topic, qualitylayer, other, source }) => (
              <tr key={topic}><th scope="row">{topic}</th><td>{qualitylayer}</td><td>{other} <a href={`#source-${source}`}>[{source}]</a></td></tr>
            ))}</tbody>
          </table>
        </div>
      </section>
      <ProofAndReview />
      <section aria-labelledby="choose">
        <h2 id="choose">Which fits your work?</h2>
        <p>{c.chooseOther}</p>
        <p>{c.chooseQualityLayer}</p>
        <p><Link to="/pricing">See QualityLayer pricing</Link> or <Link to="/download">download the App</Link> to evaluate it on your own change.</p>
      </section>
      <section aria-labelledby="related">
        <h2 id="related">Other comparisons</h2>
        <p><Link to={ROUNDUP_PATH}>Compare spec-driven development tools by use case</Link>, or <Link to="/compare">browse all comparisons</Link>.</p>
        <ComparisonLinks current={c.slug} />
      </section>
    </Frame>
  );
}

function CompareIndex() {
  return (
    <Frame title="Compare QualityLayer" lead="Choose a workflow for planning, building and reviewing agent-written code. These comparisons explain the overlap, each tool's strengths and where QualityLayer puts your attention." sources={[COMPARISONS[0].sources[1], COMPARISONS[1].sources[2], COMPARISONS[2].sources[2], COMPARISONS[3].sources[2]]}>
      <section aria-labelledby="comparisons">
        <h2 id="comparisons">Compare one tool at a time</h2>
        <ComparisonLinks />
      </section>
      <section aria-labelledby="start">
        <h2 id="start">Start with your review process</h2>
        <p>Supporting Claude Code and Codex is common ground: HumanLayer's portable RPI skills, GitHub Spec Kit and OpenSpec also work in these agents. Kiro offers its own coding environment, including a CLI.</p>
        <p>The useful questions are what you approve before code, how the implementation gets checked and what evidence reaches the reviewer. Each detailed comparison links to the documentation behind its claims.</p>
        <p><Link to={ROUNDUP_PATH}>Read the spec-driven development tools guide</Link> for a comparison by use case, including how to verify AI generated code.</p>
      </section>
      <ProofAndReview />
      <p className="cp-next"><Link to="/pricing">QualityLayer pricing</Link><Link to="/docs/steps/verify" reloadDocument>Explore Verify</Link></p>
    </Frame>
  );
}

function Roundup() {
  const bySlug = (slug: string) => COMPARISONS.find((c) => c.slug === slug)!;
  const tools = [
    { slug: "spec-kit", fit: "A process your team can customize", note: "Specifications, plans and tasks with configurable extensions and presets. Converge checks the implementation against those artifacts." },
    { slug: "humanlayer", fit: "Shared planning and agent sessions", note: "Collaborative workspaces, inline design discussions and portable RPI skills for Claude Code and Codex." },
    { slug: "kiro", fit: "Specs in an integrated coding environment", note: "Requirements, designs and tasks in Kiro. The IDE includes property-based testing; capabilities vary across its surfaces." },
    { slug: "openspec", fit: "Evolving specs in an existing repository", note: "Change proposals and spec deltas, with flexible artifact editing, optional verification and archiving into the main specs." },
  ];
  const sources = COMPARISONS.flatMap((c) => c.sources);
  return (
    <Frame title="Best spec-driven development tools for your workflow" lead="The best fit depends on where you want structure: writing specs, coordinating agents or reviewing evidence. Here is how QualityLayer, HumanLayer, GitHub Spec Kit, OpenSpec and Kiro approach that work." sources={sources} faq>
      <section aria-labelledby="criteria">
        <h2 id="criteria">How to choose</h2>
        <p>Compare the tools on the same change: define an outcome, inspect the plan, build it and ask what proves it works. This guide uses the public docs linked below. It assigns no scores or performance ranking.</p>
        <p>Ask where the specs live, which agent executes the work, who checks the implementation and what happens when a check cannot run. Human approval and a useful AI code review process depend on those details.</p>
      </section>
      <section aria-labelledby="tools">
        <h2 id="tools">Tools by use case</h2>
        <div className="cp-table-scroll" role="region" aria-label="Spec-driven development tools by use case" tabIndex={0}>
          <table>
            <caption>A starting point for evaluating your own workflow</caption>
            <thead><tr><th scope="col">Tool</th><th scope="col">Consider it for</th><th scope="col">What the docs describe</th></tr></thead>
            <tbody>
              {tools.map(({ slug, fit, note }) => <tr key={slug}><th scope="row"><Link to={`/compare/${slug}`}>{bySlug(slug).name}</Link></th><td>{fit}</td><td>{note} <a href={bySlug(slug).sources[0].url}>Docs</a>{slug === "kiro" && <> · <a href={bySlug(slug).sources[1].url}>Testing</a></>}{slug === "openspec" && <> · <a href={bySlug(slug).sources[1].url}>Verification</a></>}</td></tr>)}
              <tr><th scope="row"><Link to="/">QualityLayer</Link></th><td>Visual planning and human review with recorded proof</td><td>Approve the Plan, check agreed outcomes in Verify and review the evidence before opening a pull request. <a href="/docs/steps/review">Docs</a></td></tr>
            </tbody>
          </table>
        </div>
      </section>
      <section aria-labelledby="agent-fit">
        <h2 id="agent-fit">Keeping Claude Code or Codex</h2>
        <p>QualityLayer, <a href="https://github.com/humanlayer/skills#rpi">HumanLayer's RPI skills</a>, <a href="https://github.github.io/spec-kit/reference/integrations.html">Spec Kit</a> and <a href="https://openspec.dev/docs/supported-tools">OpenSpec</a> all support Claude Code and Codex. This is an overlap to evaluate honestly.</p>
        <p><a href="https://kiro.dev/docs/specs/">Kiro's docs</a> describe specs across its own IDE, CLI and web surfaces. Consider Kiro if you want that integrated environment; compare the other options if you want a process in your existing agent session.</p>
      </section>
      <section aria-labelledby="verify-code">
        <h2 id="verify-code">How to verify AI generated code</h2>
        <p>A specification makes intent reviewable. To check the result, turn acceptance criteria into observable behavior, run your project's tests, types, lint and build, then exercise the relevant behavior in the running program.</p>
        <p>Keep the evidence with the change. A review should distinguish checks that passed, checks that failed and checks that the environment blocked. Ask whether the reviewer wrote the code and whether a second reviewer is required for the risk involved.</p>
        <p>The tools overlap here too. <a href="https://github.github.io/spec-kit/reference/agentic-sdd.html">Spec Kit has convergence checks</a>; <a href="https://openspec.dev/docs/skills#openspec-verify-change">OpenSpec has optional verification</a>; <a href="https://kiro.dev/docs/specs/correctness/">Kiro documents property-based testing in its IDE</a>. Compare the evidence and approval process around those checks.</p>
      </section>
      <ProofAndReview />
      <section aria-labelledby="questions">
        <h2 id="questions">Common questions</h2>
        {ROUNDUP_FAQS.map(({ question, answer }) => <div key={question}><h3>{question}</h3><p>{answer}</p></div>)}
      </section>
      <section aria-labelledby="next">
        <h2 id="next">Evaluate it on a real change</h2>
        <p>Use a task with a testable outcome and an edge case. Compare how much you understand before implementation and what you can verify afterward.</p>
        <p><Link to="/compare">Read the detailed comparisons</Link>, explore <a href="/docs/steps/verify">Verify</a> and <a href="/docs/steps/review">Review</a>, or check <Link to="/pricing">QualityLayer pricing</Link>.</p>
      </section>
    </Frame>
  );
}

export default function Compare() {
  const { pathname } = useLocation();
  if (pathname === ROUNDUP_PATH) return <Roundup />;
  const comparison = COMPARISONS.find(({ slug }) => pathname === `/compare/${slug}`);
  return comparison ? <HeadToHead comparison={comparison} /> : <CompareIndex />;
}
