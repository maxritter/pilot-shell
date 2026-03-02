import { useState, useCallback, useEffect, useRef } from "react";
import { useTeams } from "../../hooks/useTeams";
import { useLicense } from "../../hooks/useLicense";
import { useToast } from "../../context/ToastContext";
import { Icon, Badge, EmptyState } from "../../components/ui";
import { TeamGate } from "../../components/TeamGate";
import { TeamsSummaryCards } from "./TeamsSummaryCards";
import { TeamsAssetTable } from "./TeamsAssetTable";
import { TeamsPushPanel } from "./TeamsPushPanel";
import { TeamsSetupTab } from "./TeamsSetupTab";

function formatRepoUrl(url: string): string {
  try {
    const u = new URL(url);
    return (u.host + u.pathname).replace(/\.git$/, "");
  } catch {
    return url;
  }
}

export function TeamsView() {
  const {
    teamsStatus,
    mergedAssets,
    isLoading,
    error,
    fetchDetail,
    detailCache,
    loadingDetails,
    installAll,
    isInstalling,
    installError,
    discover,
    pushAsset,
    refresh,
    initTeams,
    removeAsset,
    updateAsset,
  } = useTeams();

  const { license } = useLicense();
  const toast = useToast();
  const prevInstallingRef = useRef(isInstalling);

  const [showPushPanel, setShowPushPanel] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeAssetFilter, setActiveAssetFilter] = useState("all");
  const [expandedAsset, setExpandedAsset] = useState<string | null>(null);

  const handleInstall = useCallback(() => {
    installAll();
  }, [installAll]);

  const handleAssetClick = useCallback((name: string) => {
    setExpandedAsset((prev) => (prev === name ? null : name));
  }, []);

  const handleUpdate = useCallback(
    async (asset: {
      name: string;
      installedVersion: string | null;
      scope: string | null;
    }) => {
      toast.info(`Updating ${asset.name}...`, "Update Started");
      const result = await updateAsset(
        asset.name,
        asset.installedVersion ?? "",
        asset.scope === "Global" ? "global" : "project",
        asset.scope !== "Global" ? asset.scope : null,
      );
      if (result.success) {
        toast.success(`Updated ${asset.name}`, "Update Complete");
      } else {
        toast.error(result.error || "Update failed", "Update Failed");
      }
    },
    [updateAsset, toast],
  );

  const handleRemove = useCallback(
    async (name: string) => {
      const result = await removeAsset(name);
      if (result.success) {
        toast.success(`Removed ${name}`, "Removed");
        refresh();
      } else {
        toast.error(result.error || "Remove failed", "Remove Failed");
      }
    },
    [removeAsset, refresh, toast],
  );

  useEffect(() => {
    const wasInstalling = prevInstallingRef.current;
    const nowInstalling = isInstalling;

    if (wasInstalling && !nowInstalling) {
      if (installError) {
        if (installError.includes("longer than expected")) {
          toast.warning(installError, "Install Timeout");
        } else {
          toast.error(installError, "Install Failed");
        }
      } else {
        toast.success("Teams synced successfully", "Sync Complete");
      }
    }

    prevInstallingRef.current = isInstalling;
  }, [isInstalling, installError, toast]);

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="flex items-baseline gap-3">
          <h1 className="text-2xl font-bold">Teams</h1>
          <span className="text-xs text-base-content/40 flex items-center gap-2">
            <span className="loading loading-spinner loading-xs" />
            Loading teams data...
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="stats shadow bg-base-200 animate-pulse">
              <div className="stat">
                <div className="h-3 bg-base-300 rounded w-20 mb-2" />
                <div className="h-8 bg-base-300 rounded w-24 mb-1" />
                <div className="h-3 bg-base-300 rounded w-16" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <h1 className="text-2xl font-bold">Teams</h1>
        <div className="alert alert-error">
          <span>Failed to load teams data: {error}</span>
        </div>
      </div>
    );
  }

  if (!teamsStatus?.installed) {
    return (
      <div className="space-y-8">
        <h1 className="text-2xl font-bold">Teams</h1>
        <EmptyState
          icon="lucide:users"
          title="sx is not installed"
          description="Install sx to share skills, rules, and commands with your team."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Teams</h1>
          {teamsStatus.configured && (
            <Badge variant="success" size="sm">
              Connected
            </Badge>
          )}
          {teamsStatus.version && (
            <Badge variant="ghost" size="sm">
              sx v{teamsStatus.version}
            </Badge>
          )}
          {installError && (
            <span className="text-xs text-warning">{installError}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <TeamGate tier={license?.tier ?? null} featureName="Push assets">
            <button
              className={`btn btn-sm gap-2 ${showPushPanel ? "btn-secondary" : "btn-outline"}`}
              onClick={() => setShowPushPanel((v) => !v)}
            >
              <Icon icon="lucide:upload" size={14} />
              Push Local
            </button>
          </TeamGate>
          <TeamsSyncButton
            isInstalling={isInstalling}
            onInstall={handleInstall}
          />
        </div>
      </div>

      {/* Repo URL */}
      {teamsStatus.configured && teamsStatus.repoUrl && (
        <div className="flex items-center gap-2 text-sm text-base-content/60">
          <Icon icon="lucide:git-branch" size={16} />
          <span className="font-mono text-xs">
            {formatRepoUrl(teamsStatus.repoUrl)}
          </span>
        </div>
      )}

      {/* Push panel (conditionally shown) */}
      {showPushPanel && (
        <TeamGate tier={license?.tier ?? null} featureName="Push assets">
          <TeamsPushPanel
            discover={discover}
            pushAsset={pushAsset}
            onPushComplete={() => {
              refresh();
              setShowPushPanel(false);
            }}
          />
        </TeamGate>
      )}

      {/* Summary cards */}
      <TeamsSummaryCards assets={mergedAssets} />

      {/* Asset table */}
      {mergedAssets.length === 0 ? (
        <EmptyState
          icon="lucide:package"
          title="No assets in catalog"
          description="Push skills, rules, or commands to your team repository."
        />
      ) : (
        <TeamsAssetTable
          assets={mergedAssets}
          searchQuery={searchQuery}
          activeTab={activeAssetFilter}
          onTabChange={setActiveAssetFilter}
          onSearchChange={setSearchQuery}
          expandedAsset={expandedAsset}
          onAssetClick={handleAssetClick}
          fetchDetail={fetchDetail}
          detailCache={detailCache}
          loadingDetails={loadingDetails}
          tier={license?.tier ?? null}
          onUpdate={handleUpdate}
          onRemove={handleRemove}
        />
      )}

      {/* Repository configuration section */}
      <div className="divider text-xs text-base-content/40">
        Repository Setup
      </div>
      <TeamGate tier={license?.tier ?? null} featureName="Repository setup">
        <TeamsSetupTab teamsStatus={teamsStatus} initTeams={initTeams} />
      </TeamGate>
    </div>
  );
}

function TeamsSyncButton({
  isInstalling,
  onInstall,
}: {
  isInstalling: boolean;
  onInstall: () => void;
}) {
  return (
    <button
      className="btn btn-primary btn-sm"
      disabled={isInstalling}
      onClick={onInstall}
    >
      {isInstalling ? (
        <>
          <span className="loading loading-spinner loading-xs" />
          Syncing...
        </>
      ) : (
        <>
          <Icon icon="lucide:refresh-cw" size={14} />
          Sync All
        </>
      )}
    </button>
  );
}
