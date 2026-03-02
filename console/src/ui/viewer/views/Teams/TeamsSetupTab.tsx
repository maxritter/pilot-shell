import { useState } from "react";
import { Icon, Badge } from "../../components/ui";
import type { PushResult } from "../../hooks/useTeams";
import type { TeamsStatus } from "../../hooks/useStats";

interface TeamsSetupTabProps {
  teamsStatus: TeamsStatus;
  initTeams: (type: string, repoUrl: string) => Promise<PushResult>;
}

const REPO_TYPES = [
  { id: "git", label: "Git Repository", icon: "lucide:git-branch" },
  { id: "path", label: "Local Directory", icon: "lucide:folder" },
  { id: "sleuth", label: "Skills.new", icon: "lucide:cloud" },
];

export function TeamsSetupTab({ teamsStatus, initTeams }: TeamsSetupTabProps) {
  const [repoType, setRepoType] = useState("git");
  const [repoUrl, setRepoUrl] = useState("");
  const [isInitializing, setIsInitializing] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  const [isReconfiguring, setIsReconfiguring] = useState(false);

  const handleInit = async () => {
    if (!repoUrl.trim()) return;
    setIsInitializing(true);
    setInitError(null);
    const result = await initTeams(repoType, repoUrl.trim());
    setIsInitializing(false);
    if (result.success) {
      setIsReconfiguring(false);
      setRepoUrl("");
    } else {
      setInitError(result.error || "Initialization failed");
    }
  };

  const initForm = (
    <div className="space-y-4">
      {/* Repository type selector */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Repository Type</label>
        <div className="flex gap-2">
          {REPO_TYPES.map((t) => (
            <button
              key={t.id}
              className={`btn btn-sm gap-2 ${repoType === t.id ? "btn-primary" : "btn-ghost"}`}
              onClick={() => setRepoType(t.id)}
              disabled={isInitializing}
            >
              <Icon icon={t.icon} size={14} />
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* URL input */}
      <div className="space-y-2">
        <label className="text-sm font-medium">
          {repoType === "path" ? "Directory Path" : "Repository URL"}
        </label>
        <input
          type="text"
          className="input input-bordered w-full"
          placeholder={
            repoType === "git"
              ? "git@github.com:org/team-vault.git"
              : repoType === "path"
                ? "/path/to/vault"
                : "https://skills.new/..."
          }
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          disabled={isInitializing}
        />
      </div>

      {initError && (
        <div className="alert alert-error py-2">
          <span className="text-sm">{initError}</span>
        </div>
      )}

      <div className="flex gap-2">
        <button
          className="btn btn-primary btn-sm"
          disabled={!repoUrl.trim() || isInitializing}
          onClick={handleInit}
        >
          {isInitializing ? (
            <>
              <span className="loading loading-spinner loading-xs" />
              Initializing...
            </>
          ) : (
            <>
              <Icon icon="lucide:check" size={14} />
              Initialize
            </>
          )}
        </button>
        {isReconfiguring && (
          <button
            className="btn btn-ghost btn-sm"
            disabled={isInitializing}
            onClick={() => {
              setIsReconfiguring(false);
              setInitError(null);
              setRepoUrl("");
            }}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );

  if (teamsStatus.configured && !isReconfiguring) {
    return (
      <div className="space-y-4">
        <div className="card bg-base-200">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <h3 className="card-title text-base">Repository Configuration</h3>
              <button
                className="btn btn-ghost btn-xs gap-1"
                onClick={() => setIsReconfiguring(true)}
              >
                <Icon icon="lucide:settings-2" size={12} />
                Reconfigure
              </button>
            </div>
            <div className="space-y-3 text-sm">
              {teamsStatus.repoUrl && (
                <div className="flex items-center gap-2">
                  <Icon
                    icon="lucide:git-branch"
                    size={16}
                    className="text-base-content/50"
                  />
                  <span className="text-base-content/60">URL:</span>
                  <span className="font-mono text-xs">
                    {teamsStatus.repoUrl}
                  </span>
                </div>
              )}
              {teamsStatus.version && (
                <div className="flex items-center gap-2">
                  <Icon
                    icon="lucide:package"
                    size={16}
                    className="text-base-content/50"
                  />
                  <span className="text-base-content/60">sx version:</span>
                  <Badge variant="ghost" size="sm">
                    {teamsStatus.version}
                  </Badge>
                </div>
              )}
              {teamsStatus.profile && (
                <div className="flex items-center gap-2">
                  <Icon
                    icon="lucide:user"
                    size={16}
                    className="text-base-content/50"
                  />
                  <span className="text-base-content/60">Profile:</span>
                  <span>{teamsStatus.profile}</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Icon
                  icon="lucide:package"
                  size={16}
                  className="text-base-content/50"
                />
                <span className="text-base-content/60">Assets installed:</span>
                <span className="font-semibold">
                  {teamsStatus.assets.length}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Icon
                  icon="lucide:cloud"
                  size={16}
                  className="text-base-content/50"
                />
                <span className="text-base-content/60">Assets in catalog:</span>
                <span className="font-semibold">
                  {teamsStatus.catalog.length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="card bg-base-200">
        <div className="card-body">
          <h3 className="card-title text-base">
            {isReconfiguring
              ? "Reconfigure Repository"
              : "Initialize Repository"}
          </h3>
          <p className="text-sm text-base-content/60">
            {isReconfiguring
              ? "Enter a new repository URL to switch your team repository."
              : "Set up a repository to share skills, rules, and commands with your team."}
          </p>
          <div className="mt-4">{initForm}</div>
        </div>
      </div>
    </div>
  );
}
