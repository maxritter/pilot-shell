import { Bot, Terminal } from "lucide-react";

const MonoName = ({ children }: { children: string }) => (
  <span className="ps-mono">{children}</span>
);

const AgentsSection = () => (
  <section className="ps-sec" id="agents" aria-labelledby="agents-heading">
    <div className="ps-ctr">
      <div className="ps-sec-hd ps-left ps-rv">
        <h2 className="ps-h2" id="agents-heading">
          Supported agents
        </h2>
      </div>

      <div className="ps-ag ps-stg">
        <div>
          <div className="ps-ag-hd">
            <span className="ps-tile">
              <Bot className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <h3 className="ps-h3">Claude Code</h3>
              <p className="ps-sup" style={{ marginTop: 2 }}>
                Primary — full feature coverage
              </p>
            </div>
          </div>
          <p className="ps-body">
            All workflows, lifecycle hooks, model switching (Opus plans, Sonnet
            executes), language servers, and the complete Console integration.
            Requires a Claude Max, Team Premium, or Enterprise subscription.
          </p>
        </div>

        <div>
          <div className="ps-ag-hd">
            <span className="ps-tile">
              <Terminal className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <h3 className="ps-h3">Codex</h3>
              <p className="ps-sup" style={{ marginTop: 2 }}>
                All workflows, fewer platform features
              </p>
            </div>
          </div>
          <p className="ps-body">
            Via Codex CLI or the ChatGPT desktop app — <MonoName>$prd</MonoName>,{" "}
            <MonoName>$spec</MonoName>, <MonoName>$build</MonoName>, and{" "}
            <MonoName>$fix</MonoName> are explicit-only; native /goal, safety
            settings, and bounded subagents stay available. Requires an OpenAI
            Plus, Pro, Business, or Enterprise subscription.
          </p>
        </div>
      </div>
    </div>
  </section>
);

export default AgentsSection;
