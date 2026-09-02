import { Bell, Link2, Users, type LucideIcon } from "lucide-react";

const reviewerFeatures: Array<{ icon: LucideIcon; title: string; desc: string }> = [
  {
    icon: Link2,
    title: "One link, many reviewers",
    desc: "Click Share with Teammates once and forward the link to as many people as you like — no Pilot install required on their side.",
  },
  {
    icon: Users,
    title: "Feedback grouped by author",
    desc: "Teammate annotations stream back into your Console in 60 seconds — stored next to the spec, so the agent reads them at the next review checkpoint.",
  },
  {
    icon: Bell,
    title: "Zero handoff overhead",
    desc: "Reviewers click Submit — no copy-URL-back step. Each submit lands as a single notification in your Console.",
  },
];

const SpecReviewMock = () => (
  <div className="ps-win" aria-hidden="true">
    <div className="ps-win-bar">
      <div className="ps-dots">
        <span style={{ background: "hsl(0 60% 55%)" }} />
        <span style={{ background: "hsl(40 80% 55%)" }} />
        <span style={{ background: "hsl(140 50% 45%)" }} />
      </div>
      <span className="ps-url">pilot-shell.com/s/rate-limiting</span>
    </div>
    <div className="ps-spec">
      <p className="ps-lbl" style={{ marginBottom: 12 }}>
        Specification — rate limiting
      </p>
      <div className="ps-spec-l">1. Add a token-bucket limiter to the gateway middleware</div>
      <div className="ps-spec-l ps-hi">
        2. Return 429 with a Retry-After header once the bucket is empty
      </div>
      <div className="ps-spec-l">3. Persist per-key counters in Redis with a sliding window</div>
      <div className="ps-note">
        <span className="ps-av">BK</span>
        <div>
          <p className="ps-meta">
            <span className="ps-strong">Bob K.</span> · 2m ago · on line 2
          </p>
          <p className="ps-sup" style={{ color: "var(--ps-fg)", marginTop: 2 }}>
            What happens when the client retries during a window rollover? Worth
            an explicit test.
          </p>
        </div>
      </div>
      <p className="ps-annot">
        <Bell className="h-3.5 w-3.5" aria-hidden="true" />3 annotations on
        rate-limiting — grouped by author in your Console
      </p>
    </div>
  </div>
);

const SpecCollabSection = () => (
  <section className="ps-sec" id="shift-left" aria-labelledby="shift-left-heading">
    <div className="ps-ctr">
      <div className="ps-sec-hd ps-rv">
        <p className="ps-eyebrow">Shift left</p>
        <h2 className="ps-h2" id="shift-left-heading">
          Catch flaws in the spec, not the PR.
        </h2>
        <p className="ps-lead">
          Review and annotate requirements with your team{" "}
          <span className="ps-strong">before a single line of code is written</span>.
          Wrong approach, missed edge case, unclear scope, weak architecture —
          spot it while it costs a sentence to change, not a refactor.
        </p>
      </div>

      <div className="ps-matrix ps-rv">
        <div className="ps-mcell">
          <SpecReviewMock />
        </div>
        <div className="ps-mcol">
          {reviewerFeatures.map((feature) => (
            <div key={feature.title} className="ps-mrow">
              <span className="ps-tile">
                <feature.icon className="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <h3 className="ps-h4">{feature.title}</h3>
                <p className="ps-sup" style={{ marginTop: 8 }}>
                  {feature.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

export default SpecCollabSection;
