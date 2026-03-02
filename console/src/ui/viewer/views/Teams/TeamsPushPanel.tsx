import { useState, useEffect, useCallback } from "react";
import { Icon, Badge, EmptyState } from "../../components/ui";
import type {
  DiscoveredAsset,
  DiscoverResult,
  PushResult,
} from "../../hooks/useTeams";

interface TeamsPushPanelProps {
  discover: () => Promise<DiscoverResult>;
  pushAsset: (
    asset: DiscoveredAsset,
    scope: string,
    scopeUrl: string | null,
  ) => Promise<PushResult>;
  onPushComplete: () => void;
}

const TYPE_ICONS: Record<string, string> = {
  skill: "lucide:wand-2",
  rule: "lucide:scale",
  command: "lucide:terminal",
};

export function TeamsPushPanel({
  discover,
  pushAsset,
  onPushComplete,
}: TeamsPushPanelProps) {
  const [assets, setAssets] = useState<DiscoveredAsset[]>([]);
  const [repoUrl, setRepoUrl] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [scope, setScope] = useState<"project" | "global">("project");
  const [isLoading, setIsLoading] = useState(true);
  const [isPushing, setIsPushing] = useState(false);
  const [pushResults, setPushResults] = useState<
    Map<string, { success: boolean; error: string | null }>
  >(new Map());

  useEffect(() => {
    let mounted = true;
    setIsLoading(true);
    discover().then((result) => {
      if (!mounted) return;
      setAssets(result.assets);
      setRepoUrl(result.repoUrl);
      setIsLoading(false);
    });
    return () => {
      mounted = false;
    };
  }, [discover]);

  const toggleSelection = useCallback((name: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  }, []);

  const toggleAll = useCallback(() => {
    setSelected((prev) => {
      if (prev.size === assets.length) return new Set();
      return new Set(assets.map((a) => a.name));
    });
  }, [assets]);

  const handlePush = useCallback(async () => {
    if (selected.size === 0) return;
    setIsPushing(true);
    setPushResults(new Map());

    const scopeUrl = scope === "project" ? repoUrl : null;
    const selectedAssets = assets.filter((a) => selected.has(a.name));
    const localResults = new Map<
      string,
      { success: boolean; error: string | null }
    >();

    for (const asset of selectedAssets) {
      const result = await pushAsset(asset, scope, scopeUrl);
      localResults.set(asset.name, result);
      setPushResults(new Map(localResults));
    }

    setIsPushing(false);
    const allSucceeded = selectedAssets.every(
      (a) => localResults.get(a.name)?.success,
    );
    if (allSucceeded) {
      onPushComplete();
    }
  }, [selected, assets, scope, repoUrl, pushAsset, onPushComplete]);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 py-8 justify-center text-base-content/50">
        <span className="loading loading-spinner loading-sm" />
        Discovering local assets...
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <EmptyState
        icon="lucide:upload"
        title="No local assets to push"
        description="Create skills, rules, or commands in .claude/ first."
      />
    );
  }

  return (
    <div className="space-y-4 border border-base-300 rounded-lg p-4 bg-base-200/30">
      {/* Scope selector */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium">Push to:</span>
        <div className="flex gap-2">
          <label className="label cursor-pointer gap-2">
            <input
              type="radio"
              name="push-scope"
              className="radio radio-sm radio-primary"
              checked={scope === "project"}
              onChange={() => setScope("project")}
              disabled={isPushing}
            />
            <span className="text-sm">Project</span>
          </label>
          <label className="label cursor-pointer gap-2">
            <input
              type="radio"
              name="push-scope"
              className="radio radio-sm radio-primary"
              checked={scope === "global"}
              onChange={() => setScope("global")}
              disabled={isPushing}
            />
            <span className="text-sm">Global</span>
          </label>
        </div>
        {scope === "project" && repoUrl && (
          <span className="text-xs text-base-content/40 font-mono truncate max-w-xs">
            {repoUrl}
          </span>
        )}
      </div>

      {/* Asset list */}
      <div className="overflow-x-auto">
        <table className="table w-full">
          <thead>
            <tr>
              <th className="w-10">
                <input
                  type="checkbox"
                  className="checkbox checkbox-sm"
                  checked={selected.size === assets.length}
                  onChange={toggleAll}
                  disabled={isPushing}
                />
              </th>
              <th>Name</th>
              <th>Type</th>
              <th>Path</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => {
              const result = pushResults.get(asset.name);
              return (
                <tr key={asset.name} className="hover">
                  <td>
                    <input
                      type="checkbox"
                      className="checkbox checkbox-sm"
                      checked={selected.has(asset.name)}
                      onChange={() => toggleSelection(asset.name)}
                      disabled={isPushing}
                    />
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <Icon
                        icon={TYPE_ICONS[asset.type] || "lucide:package"}
                        size={16}
                        className="text-base-content/50"
                      />
                      <span className="font-medium">{asset.name}</span>
                    </div>
                  </td>
                  <td>
                    <Badge variant="ghost" size="sm">
                      {asset.type}
                    </Badge>
                  </td>
                  <td className="font-mono text-xs text-base-content/60">
                    {asset.path}
                  </td>
                  <td>
                    {result ? (
                      result.success ? (
                        <Badge variant="success" size="sm">
                          Pushed
                        </Badge>
                      ) : (
                        <span
                          className="text-xs text-error"
                          title={result.error || ""}
                        >
                          Failed
                        </span>
                      )
                    ) : isPushing && selected.has(asset.name) ? (
                      <span className="loading loading-spinner loading-xs" />
                    ) : null}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Push button */}
      <div className="flex items-center gap-4">
        <button
          className="btn btn-primary btn-sm"
          disabled={selected.size === 0 || isPushing}
          onClick={handlePush}
        >
          {isPushing ? (
            <>
              <span className="loading loading-spinner loading-xs" />
              Pushing...
            </>
          ) : (
            <>
              <Icon icon="lucide:upload" size={14} />
              Push Selected ({selected.size})
            </>
          )}
        </button>
        {pushResults.size > 0 && !isPushing && (
          <span className="text-sm text-base-content/60">
            {[...pushResults.values()].filter((r) => r.success).length} of{" "}
            {pushResults.size} pushed successfully
          </span>
        )}
      </div>
    </div>
  );
}
