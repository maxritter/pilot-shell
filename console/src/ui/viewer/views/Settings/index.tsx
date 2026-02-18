import { useState } from "react";
import {
  MODEL_CHOICES_FULL,
  MODEL_CHOICES_AGENT,
  DEFAULT_SETTINGS,
  MODEL_DISPLAY_NAMES,
  useSettings,
} from "../../hooks/useSettings.js";
import { ModelSelect } from "./ModelSelect.js";

// Source: https://platform.claude.com/docs/en/about-claude/pricing

const SPEC_COMMANDS = ["spec", "spec-plan", "spec-implement", "spec-verify"];
const GENERAL_COMMANDS = ["vault", "sync", "learn"];

const COMMAND_LABELS: Record<string, string> = {
  spec: "/spec (dispatcher)",
  "spec-plan": "/spec planning",
  "spec-implement": "/spec implement",
  "spec-verify": "/spec verify",
  vault: "/vault",
  sync: "/sync",
  learn: "/learn",
};

const AGENT_LABELS: Record<string, string> = {
  "plan-challenger": "plan-challenger",
  "plan-verifier": "plan-verifier",
  "spec-reviewer-compliance": "spec-reviewer-compliance",
  "spec-reviewer-quality": "spec-reviewer-quality",
};

function DefaultLabel({ model }: { model: string }) {
  return (
    <span className="text-xs text-base-content/40">
      {MODEL_DISPLAY_NAMES[model] ?? model}
    </span>
  );
}

export function SettingsView() {
  const {
    settings,
    isLoading,
    error,
    isDirty,
    saved,
    updateModel,
    updateCommand,
    updateAgent,
    save,
  } = useSettings();
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveError(null);
    try {
      await save();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="card bg-base-200 animate-pulse">
              <div className="card-body">
                <div className="h-4 bg-base-300 rounded w-32 mb-4" />
                <div className="h-8 bg-base-300 rounded w-48" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <div className="alert alert-error">
          <span>Failed to load settings: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-base-content/60">
          Model selection for Claude Pilot. Restart Pilot after saving to apply.
        </p>
        <p className="text-base-content/40 text-xs mt-1">
          1M context models require an Enterprise or Max (20×) subscription.
          Only select them if you already have access.
        </p>
      </div>

      {saveError && (
        <div className="alert alert-error">
          <span>{saveError}</span>
        </div>
      )}

      {/* Section 1: General — Main model + utility commands */}
      <div className="card bg-base-200">
        <div className="card-body">
          <h2 className="card-title text-base">General</h2>
          <div className="overflow-x-auto">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>Setting</th>
                  <th>Model</th>
                  <th className="text-base-content/40">Default</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <span className="font-mono text-sm">Main session</span>
                    <div className="text-xs text-base-content/50">
                      Quick Mode / direct chat
                    </div>
                  </td>
                  <td>
                    <ModelSelect
                      value={settings.model}
                      choices={MODEL_CHOICES_FULL}
                      onChange={updateModel}
                      id="main-model"
                    />
                  </td>
                  <td>
                    <DefaultLabel model={DEFAULT_SETTINGS.model} />
                  </td>
                </tr>
                {GENERAL_COMMANDS.map((cmd) => (
                  <tr key={cmd}>
                    <td>
                      <span className="font-mono text-sm">
                        {COMMAND_LABELS[cmd] ?? cmd}
                      </span>
                    </td>
                    <td>
                      <ModelSelect
                        value={
                          settings.commands[cmd] ??
                          DEFAULT_SETTINGS.commands[cmd]
                        }
                        choices={MODEL_CHOICES_FULL}
                        onChange={(model) => updateCommand(cmd, model)}
                        id={`cmd-${cmd}`}
                      />
                    </td>
                    <td>
                      <DefaultLabel model={DEFAULT_SETTINGS.commands[cmd]} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Section 2: Spec Flow — spec commands + sub-agents */}
      <div className="card bg-base-200">
        <div className="card-body">
          <h2 className="card-title text-base">Spec Flow</h2>
          <p className="text-sm text-base-content/70 mb-2">
            Defaults use Opus for planning/verification, Sonnet for execution.
          </p>

          {/* Spec commands */}
          <div className="overflow-x-auto">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>Command</th>
                  <th>Model</th>
                  <th className="text-base-content/40">Default</th>
                </tr>
              </thead>
              <tbody>
                {SPEC_COMMANDS.map((cmd) => (
                  <tr key={cmd}>
                    <td>
                      <span className="font-mono text-sm">
                        {COMMAND_LABELS[cmd] ?? cmd}
                      </span>
                    </td>
                    <td>
                      <ModelSelect
                        value={
                          settings.commands[cmd] ??
                          DEFAULT_SETTINGS.commands[cmd]
                        }
                        choices={MODEL_CHOICES_FULL}
                        onChange={(model) => updateCommand(cmd, model)}
                        id={`cmd-${cmd}`}
                      />
                    </td>
                    <td>
                      <DefaultLabel model={DEFAULT_SETTINGS.commands[cmd]} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Sub-agents */}
          <h3 className="text-sm font-semibold mt-4 mb-1">Sub-Agents</h3>
          <p className="text-xs text-base-content/50 mb-2">
            1M context not available for sub-agents.
          </p>
          <div className="overflow-x-auto">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>Agent</th>
                  <th>Model</th>
                  <th className="text-base-content/40">Default</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(DEFAULT_SETTINGS.agents).map((agent) => (
                  <tr key={agent}>
                    <td>
                      <span className="font-mono text-sm">
                        {AGENT_LABELS[agent] ?? agent}
                      </span>
                    </td>
                    <td>
                      <ModelSelect
                        value={
                          settings.agents[agent] ??
                          DEFAULT_SETTINGS.agents[agent]
                        }
                        choices={MODEL_CHOICES_AGENT}
                        onChange={(model) => updateAgent(agent, model)}
                        id={`agent-${agent}`}
                      />
                    </td>
                    <td>
                      <DefaultLabel model={DEFAULT_SETTINGS.agents[agent]} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Pricing reference — collapsible */}
      <details className="collapse collapse-arrow bg-base-200 rounded-lg">
        <summary className="collapse-title text-sm font-medium py-3 min-h-0">
          Pricing reference
        </summary>
        <div className="collapse-content text-xs text-base-content/50">
          <div className="grid grid-cols-2 gap-x-6 gap-y-0.5 mb-2">
            <span>
              <span className="font-mono">Sonnet 4.6</span> — $3 / $15 per MTok
            </span>
            <span>
              <span className="font-mono">Opus 4.6</span> — $5 / $25 per MTok
            </span>
            <span>
              <span className="font-mono">Sonnet 4.6 1M</span> — $3‑6 /
              $15‑22.50
            </span>
            <span>
              <span className="font-mono">Opus 4.6 1M</span> — $5‑10 / $25‑37.50
            </span>
          </div>
          <p className="text-base-content/40">
            1M variants use standard rates up to 200K tokens, then 2× input /
            1.5× output above. Requires Max or Enterprise subscription.
          </p>
        </div>
      </details>

      {/* Sticky save bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-base-100 border-t border-base-300 px-6 py-3 flex items-center gap-4 z-50">
        <button
          className={`btn btn-primary btn-sm ${isSaving ? "loading" : ""}`}
          onClick={handleSave}
          disabled={isSaving || !isDirty}
        >
          {isSaving ? "Saving..." : "Save Settings"}
        </button>
        {isDirty && !saved && (
          <span className="text-sm text-base-content/50">Unsaved changes</span>
        )}
        {saved && (
          <span className="text-sm text-success">
            Saved — restart Pilot to apply
          </span>
        )}
      </div>
    </div>
  );
}
