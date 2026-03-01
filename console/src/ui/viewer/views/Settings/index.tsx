import { useState } from "react";
import {
  MODEL_CHOICES,
  DEFAULT_SETTINGS,
  MODEL_DISPLAY_NAMES,
  useSettings,
} from "../../hooks/useSettings.js";
import { ModelSelect } from "./ModelSelect.js";
import { ExtendedContextToggle } from "./ExtendedContextToggle.js";

const GENERAL_ROWS: { key: string; label: string; sub?: string }[] = [
  { key: "main", label: "Main session", sub: "Quick Mode / direct chat" },
  { key: "vault", label: "/vault" },
  { key: "sync", label: "/sync" },
  { key: "learn", label: "/learn" },
];

const SPEC_ROWS: { key: string; label: string }[] = [
  { key: "spec", label: "/spec (dispatcher)" },
  { key: "spec-plan", label: "/spec planning" },
  { key: "spec-implement", label: "/spec implement" },
  { key: "spec-verify", label: "/spec verify" },
];

const AGENT_ROWS: { key: string; label: string }[] = [
  { key: "plan-reviewer", label: "plan-reviewer" },
  { key: "spec-reviewer", label: "spec-reviewer" },
];

function DefaultBadge({ model }: { model: string }) {
  return (
    <span className="text-xs text-base-content/40">
      {MODEL_DISPLAY_NAMES[model] ?? model}
    </span>
  );
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <tr>
      <td
        colSpan={3}
        className="font-semibold text-sm pt-5 pb-1 px-0 border-b border-base-300"
      >
        {children}
      </td>
    </tr>
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
    updateExtendedContext,
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
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Settings</h1>
        <div className="card bg-base-200 animate-pulse">
          <div className="card-body p-4">
            <div className="h-4 bg-base-300 rounded w-32 mb-3" />
            <div className="h-8 bg-base-300 rounded w-48" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Settings</h1>
        <div className="alert alert-error">
          <span>Failed to load settings: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 pb-16">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-base-content/60 text-sm">
          Model selection for Pilot Shell. Sonnet 4.6 costs $3 input / $15
          output per million tokens (MTok). Opus 4.6 costs $5 input / $25 output
          per MTok.
        </p>
      </div>

      {saveError && (
        <div className="alert alert-error py-2">
          <span>{saveError}</span>
        </div>
      )}

      {/* Restart banner — shown after save */}
      {saved && (
        <div className="alert alert-warning shadow-md">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <span className="font-medium">
            Settings saved. Restart Pilot for changes to take effect.
          </span>
        </div>
      )}

      {/* Single unified table */}
      <div className="card bg-base-200">
        <div className="card-body p-4">
          <table className="table table-sm">
            <colgroup>
              <col className="w-[45%]" />
              <col className="w-[35%]" />
              <col className="w-[20%]" />
            </colgroup>
            <thead>
              <tr>
                <th className="text-xs">Setting</th>
                <th className="text-xs">Model</th>
                <th className="text-xs text-base-content/40">Default</th>
              </tr>
            </thead>
            <tbody>
              {/* --- General --- */}
              <SectionHeader>General</SectionHeader>
              {GENERAL_ROWS.map((row) => {
                const isMain = row.key === "main";
                const value = isMain
                  ? settings.model
                  : (settings.commands[row.key] ??
                    DEFAULT_SETTINGS.commands[row.key]);
                const defaultVal = isMain
                  ? DEFAULT_SETTINGS.model
                  : DEFAULT_SETTINGS.commands[row.key];
                return (
                  <tr key={row.key}>
                    <td>
                      <span className="font-mono text-sm">{row.label}</span>
                      {row.sub && (
                        <div className="text-xs text-base-content/50">
                          {row.sub}
                        </div>
                      )}
                    </td>
                    <td>
                      <ModelSelect
                        value={value}
                        choices={MODEL_CHOICES}
                        onChange={
                          isMain
                            ? updateModel
                            : (m) => updateCommand(row.key, m)
                        }
                        id={isMain ? "main-model" : `cmd-${row.key}`}
                      />
                    </td>
                    <td>
                      <DefaultBadge model={defaultVal} />
                    </td>
                  </tr>
                );
              })}

              {/* --- Spec Flow --- */}
              <SectionHeader>Spec Flow</SectionHeader>
              {SPEC_ROWS.map((row) => (
                <tr key={row.key}>
                  <td>
                    <span className="font-mono text-sm">{row.label}</span>
                  </td>
                  <td>
                    <ModelSelect
                      value={
                        settings.commands[row.key] ??
                        DEFAULT_SETTINGS.commands[row.key]
                      }
                      choices={MODEL_CHOICES}
                      onChange={(m) => updateCommand(row.key, m)}
                      id={`cmd-${row.key}`}
                    />
                  </td>
                  <td>
                    <DefaultBadge model={DEFAULT_SETTINGS.commands[row.key]} />
                  </td>
                </tr>
              ))}

              {/* --- Sub-Agents --- */}
              <SectionHeader>Sub-Agents</SectionHeader>
              {AGENT_ROWS.map((row) => (
                <tr key={row.key}>
                  <td>
                    <span className="font-mono text-sm">{row.label}</span>
                  </td>
                  <td>
                    <ModelSelect
                      value={
                        settings.agents[row.key] ??
                        DEFAULT_SETTINGS.agents[row.key]
                      }
                      choices={MODEL_CHOICES}
                      onChange={(m) => updateAgent(row.key, m)}
                      id={`agent-${row.key}`}
                    />
                  </td>
                  <td>
                    <DefaultBadge model={DEFAULT_SETTINGS.agents[row.key]} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <ExtendedContextToggle
        enabled={settings.extendedContext}
        onChange={updateExtendedContext}
      />

      {/* Sticky save bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-base-100 border-t border-base-300 px-6 py-2 flex items-center gap-4 z-50">
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
          <span className="text-sm text-warning">Restart Pilot to apply</span>
        )}
      </div>
    </div>
  );
}
