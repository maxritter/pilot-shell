import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import InstallCommand from "@/components/InstallCommand";
import Questions from "@/components/Questions";
import { useNarrow } from "@/hooks/useNarrow";
import { FAQS } from "@/lib/content";
import CockpitTour from "./CockpitTour";
import Crew from "./Crew";
import { useDemoTour } from "./demoTour";
import Films from "./Films";
import Lifecycle from "./Lifecycle";
import Peers from "./Peers";
import PlanTeam from "./PlanTeam";
import ReviewTeam from "./ReviewTeam";
import TwoWays from "./TwoWays";

function Section({ id, title, lead, sunk, children }: { id: string; title: string; lead: string; sunk?: boolean; children: ReactNode }) {
  return (
    <section id={id} className={`w7-sec${sunk ? " w7-sunk" : ""}`} aria-labelledby={`${id}-h`}>
      <div className="w7-wrap">
        <h2 id={`${id}-h`} className="w7-h2">{title}</h2>
        <p className="w7-lead">{lead}</p>
        <div className="w7-figure">{children}</div>
      </div>
    </section>
  );
}

export default function Sections() {
  const narrow = useNarrow();
  const tour = useDemoTour();
  return (
    <>
      <Films />
      {narrow ? null : <CockpitTour />}
      <Lifecycle />
      <Section id="plan" sunk title="Shift left: agree on the design before any code" lead="Diagrams, mockups and comments while it is still a document. No code exists until you approve.">
        <TwoWays part="plan" />
      </Section>
      <Section id="build" title="Built in vertical slices, checked end to end" lead="Each slice goes through every layer, starts with a failing test, and runs end to end before the next one starts.">
        <TwoWays part="build" />
      </Section>
      <Crew />
      <Section id="peers" title="Claude Code and Codex sessions talk to each other" lead="Ask another session for a review, hand over a task, or talk a problem through, in any direction.">
        <Peers />
      </Section>
      <Section id="team" sunk title="Review the plan as a team" lead="Teammates comment and approve in their own App while the plan is still cheap to change. Their feedback goes to your agent; you decide.">
        <PlanTeam onOpen={narrow ? undefined : () => tour.go("team")} />
      </Section>
      <Section id="review" title="Review the change as a team" lead="Your team reviews why and how the change was made, with the proof. The code goes through your pull request, as always.">
        <ReviewTeam />
      </Section>
      <Questions faqs={FAQS} />
      <section id="install" className="w7-install" aria-labelledby="install-h">
        <div className="w7-wrap">
          <h2 className="w7-h2" id="install-h">Install QualityLayer</h2>
          <p>Installs the command-line tool and the skill for your agents. Then describe a change to your agent in any repository, and it opens the QualityLayer App.</p>
          <InstallCommand />
          <p className="w7-install-note">macOS, Linux and Windows · Terminal, desktop app or IDE · 7-day trial · <Link to="/pricing">See pricing</Link></p>
        </div>
      </section>
    </>
  );
}
