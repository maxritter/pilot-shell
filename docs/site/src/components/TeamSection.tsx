import { Brain, GitBranch, ShieldCheck, type LucideIcon } from "lucide-react";

const teamPoints: Array<{ icon: LucideIcon; title: string; desc: string }> = [
  {
    icon: Brain,
    title: "Team memories",
    desc: "Decisions, discoveries, and bugfixes persist across sessions and travel through the project repo to the whole team.",
  },
  {
    icon: GitBranch,
    title: "Extension sharing",
    desc: "Skills, rules, commands, and agents move between machines and teammates with git push and pull, managed in the Console.",
  },
  {
    icon: ShieldCheck,
    title: "One standard for everyone",
    desc: "The same plans, gates, and verification hold across sessions, projects, and teammates.",
  },
];

/* A terminal stays dark in both site themes — the palette lives in site.css. */
const GitTerminalMock = () => (
  <div className="ps-term" aria-hidden="true">
    <div className="ps-term-bar">
      <div className="ps-dots">
        <span style={{ background: "hsl(0 60% 55%)" }} />
        <span style={{ background: "hsl(40 80% 55%)" }} />
        <span style={{ background: "hsl(140 50% 45%)" }} />
      </div>
      <span className="ps-term-title">zsh — api-service</span>
    </div>
    <div className="ps-term-body">
      <div className="ps-tl">
        <span className="ps-g ps-t-blue">$</span>
        <span className="ps-t-fg">git diff --stat</span>
      </div>
      <div className="ps-tl" style={{ paddingLeft: 28 }}>
        <span>
          docs/memories/payment-provider.md <span className="ps-t-green">+12</span>
        </span>
      </div>
      <div className="ps-tl" style={{ paddingLeft: 28 }}>
        <span>
          docs/memories/rate-limit-design.md <span className="ps-t-green">+18</span>
        </span>
      </div>
      <div className="ps-tl" style={{ paddingLeft: 28 }}>
        <span>
          docs/specs/rate-limiting/plan.md <span className="ps-t-green">+64</span>
        </span>
      </div>
      <div className="ps-tl ps-t-faint" style={{ paddingLeft: 28 }}>
        <span>3 files changed, 94 insertions(+)</span>
      </div>
      <div className="ps-tl">
        <span className="ps-g ps-t-blue">$</span>
        <span className="ps-t-fg">git commit -m "memories + approved spec"</span>
      </div>
      <div className="ps-tl ps-t-faint" style={{ paddingLeft: 28 }}>
        <span>teammates can recall this context in their next session</span>
      </div>
    </div>
  </div>
);

const TeamSection = () => (
  <section className="ps-sec" id="team" aria-labelledby="team-heading">
    <div className="ps-ctr">
      <div className="ps-hband ps-rv">
        <div>
          <p className="ps-eyebrow">Built for teams</p>
          <h2 className="ps-h2" id="team-heading">
            Share the why, not just the code.
          </h2>
        </div>
        <p className="ps-lead">
          Pilot stores a project's captured decisions and discoveries in the repo
          itself, so git carries them to every contributor. Claude Code loads
          memory automatically; Codex retrieves relevant history through local
          search when needed. No cloud, no clock — you review the diff and commit.
        </p>
      </div>

      <div className="ps-feat ps-rv">
        <GitTerminalMock />
        <div className="ps-pts ps-stg">
          {teamPoints.map((point) => (
            <div key={point.title} className="ps-pt">
              <span className="ps-tile">
                <point.icon className="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <h3 className="ps-h4">{point.title}</h3>
                <p className="ps-sup" style={{ marginTop: 8 }}>
                  {point.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

export default TeamSection;
