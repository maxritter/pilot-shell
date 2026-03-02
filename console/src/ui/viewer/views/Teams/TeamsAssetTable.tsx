import { useState } from "react";
import { Icon, Badge, Tabs } from "../../components/ui";
import type { MergedAsset, AssetDetail } from "../../hooks/useTeams";
import { TeamsAssetDetail } from "./TeamsAssetDetail";

const TYPE_ICONS: Record<string, string> = {
  skill: "lucide:wand-2",
  rule: "lucide:scale",
  command: "lucide:terminal",
  agent: "lucide:bot",
  hook: "lucide:webhook",
  mcp: "lucide:plug",
};

const TYPE_BADGE_VARIANT: Record<
  string,
  "primary" | "info" | "accent" | "ghost"
> = {
  skill: "primary",
  rule: "info",
  command: "accent",
  agent: "ghost",
  hook: "ghost",
  mcp: "ghost",
};

const TABS = [
  { id: "all", label: "All" },
  { id: "skill", label: "Skills" },
  { id: "rule", label: "Rules" },
  { id: "command", label: "Commands" },
  { id: "agent", label: "Agents" },
  { id: "hook", label: "Hooks" },
  { id: "mcp", label: "MCP" },
];

interface TeamsAssetTableProps {
  assets: MergedAsset[];
  searchQuery: string;
  activeTab: string;
  onTabChange: (tab: string) => void;
  onSearchChange: (query: string) => void;
  expandedAsset: string | null;
  onAssetClick: (name: string) => void;
  fetchDetail: (name: string) => Promise<void>;
  detailCache: Map<string, AssetDetail>;
  loadingDetails: Set<string>;
  tier: string | null;
  onUpdate: (asset: MergedAsset) => void;
  onRemove: (name: string) => Promise<void>;
}

export function TeamsAssetTable({
  assets,
  searchQuery,
  activeTab,
  onTabChange,
  onSearchChange,
  expandedAsset,
  onAssetClick,
  fetchDetail,
  detailCache,
  loadingDetails,
  tier,
  onUpdate,
  onRemove,
}: TeamsAssetTableProps) {
  const filtered = assets.filter((a) => {
    const matchesTab = activeTab === "all" || a.type === activeTab;
    const matchesSearch =
      !searchQuery || a.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTab && matchesSearch;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <Tabs tabs={TABS} activeTab={activeTab} onTabChange={onTabChange} />
        <input
          type="text"
          placeholder="Search assets..."
          className="input input-bordered input-sm w-60"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-8 text-base-content/50">
          {searchQuery
            ? `No assets matching "${searchQuery}"`
            : "No assets in this category"}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Installed</th>
                <th>Latest</th>
                <th>Scope</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((asset) => (
                <AssetRow
                  key={asset.name}
                  asset={asset}
                  isExpanded={expandedAsset === asset.name}
                  onClick={() => onAssetClick(asset.name)}
                  fetchDetail={fetchDetail}
                  detail={detailCache.get(asset.name) ?? null}
                  isLoadingDetail={loadingDetails.has(asset.name)}
                  tier={tier}
                  onUpdate={onUpdate}
                  onRemove={onRemove}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AssetRow({
  asset,
  isExpanded,
  onClick,
  fetchDetail,
  detail,
  isLoadingDetail,
  tier,
  onUpdate,
  onRemove,
}: {
  asset: MergedAsset;
  isExpanded: boolean;
  onClick: () => void;
  fetchDetail: (name: string) => Promise<void>;
  detail: AssetDetail | null;
  isLoadingDetail: boolean;
  tier: string | null;
  onUpdate: (asset: MergedAsset) => void;
  onRemove: (name: string) => Promise<void>;
}) {
  const iconName = TYPE_ICONS[asset.type] ?? "lucide:package";
  const badgeVariant = TYPE_BADGE_VARIANT[asset.type] ?? "ghost";
  const [confirmRemove, setConfirmRemove] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  const handleClick = () => {
    onClick();
    if (!isExpanded && !detail && !isLoadingDetail) {
      fetchDetail(asset.name);
    }
  };

  const handleRemoveClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirmRemove) {
      setConfirmRemove(true);
      setTimeout(() => setConfirmRemove(false), 3000);
      return;
    }
    setConfirmRemove(false);
    setIsRemoving(true);
    await onRemove(asset.name);
    setIsRemoving(false);
  };

  const handleActionClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onUpdate(asset);
  };

  return (
    <>
      <tr
        className="cursor-pointer hover:bg-base-200 transition-colors"
        onClick={handleClick}
      >
        <td>
          <div className="flex items-center gap-2">
            <Icon icon={iconName} size={16} className="text-base-content/50" />
            <span className="font-medium">{asset.name}</span>
            {asset.hasUpdate && (
              <Badge variant="warning" size="sm">
                update
              </Badge>
            )}
          </div>
        </td>
        <td>
          <Badge variant={badgeVariant} size="sm">
            {asset.type}
          </Badge>
        </td>
        <td className="font-mono text-sm">
          {asset.installedVersion ?? "\u2014"}
        </td>
        <td className="font-mono text-sm">v{asset.latestVersion}</td>
        <td className="text-sm text-base-content/60">
          {asset.scope ?? "\u2014"}
        </td>
        <td onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center gap-1">
            {!asset.installed && (
              <button
                className="btn btn-ghost btn-xs gap-1"
                title="Sync all team assets to install"
                onClick={handleActionClick}
              >
                <Icon icon="lucide:download" size={12} />
                Install
              </button>
            )}
            {asset.hasUpdate && (
              <button
                className="btn btn-warning btn-xs gap-1"
                onClick={handleActionClick}
              >
                <Icon icon="lucide:refresh-cw" size={12} />
                Update
              </button>
            )}
            {asset.installed && tier === "team" && (
              <button
                className={`btn btn-xs gap-1 ${confirmRemove ? "btn-error" : "btn-ghost"}`}
                disabled={isRemoving}
                onClick={handleRemoveClick}
              >
                {isRemoving ? (
                  <span className="loading loading-spinner loading-xs" />
                ) : (
                  <>
                    <Icon
                      icon={confirmRemove ? "lucide:check" : "lucide:trash-2"}
                      size={12}
                    />
                    {confirmRemove ? "Confirm?" : "Remove"}
                  </>
                )}
              </button>
            )}
          </div>
        </td>
      </tr>
      {isExpanded && (
        <tr>
          <td colSpan={6} className="p-0">
            <TeamsAssetDetail
              detail={detail}
              isLoading={isLoadingDetail}
              onRetry={() => fetchDetail(asset.name)}
            />
          </td>
        </tr>
      )}
    </>
  );
}
