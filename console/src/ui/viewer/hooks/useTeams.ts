import { useState, useCallback, useEffect, useRef } from "react";
import type { TeamsStatus } from "./useStats";

interface TeamsAsset {
  name: string;
  version: string;
  type: string;
  clients: string[];
  status: string;
  scope: string;
}

interface TeamsCatalogItem {
  name: string;
  type: string;
  latestVersion: string;
  versionsCount: number;
  updatedAt?: string;
}

export interface MergedAsset {
  name: string;
  type: string;
  latestVersion: string;
  versionsCount: number;
  updatedAt?: string;
  installedVersion: string | null;
  installed: boolean;
  hasUpdate: boolean;
  scope: string | null;
  clients: string[];
}

export interface AssetDetail {
  name: string;
  type: string;
  metadata: {
    description: string | null;
    authors: string[];
    keywords: string[];
  };
  versions: Array<{
    version: string;
    createdAt: string | null;
    filesCount: number;
  }>;
}

export interface DiscoveredAsset {
  name: string;
  type: string;
  path: string;
}

export interface DiscoverResult {
  assets: DiscoveredAsset[];
  repoUrl: string | null;
}

export interface PushResult {
  success: boolean;
  error: string | null;
}

interface UseTeamsResult {
  teamsStatus: TeamsStatus | null;
  mergedAssets: MergedAsset[];
  isLoading: boolean;
  error: string | null;
  fetchDetail: (name: string) => Promise<void>;
  detailCache: Map<string, AssetDetail>;
  loadingDetails: Set<string>;
  detailErrors: Map<string, string>;
  installAll: () => Promise<void>;
  isInstalling: boolean;
  installError: string | null;
  refresh: () => Promise<void>;
  discover: () => Promise<DiscoverResult>;
  pushAsset: (
    asset: DiscoveredAsset,
    scope: string,
    scopeUrl: string | null,
  ) => Promise<PushResult>;
  initTeams: (type: string, repoUrl: string) => Promise<PushResult>;
  removeAsset: (name: string) => Promise<PushResult>;
  updateAsset: (
    name: string,
    currentVersion: string,
    scope: string,
    scopeUrl: string | null,
  ) => Promise<PushResult>;
}

const POLL_INTERVAL_MS = 2_000;
const MAX_POLLS = 30;

function parseVersion(v: string | null | undefined): number {
  if (!v) return NaN;
  const stripped = v.replace(/^v/i, "");
  return parseInt(stripped, 10);
}

export function mergeAssets(
  catalog: TeamsCatalogItem[],
  assets: TeamsAsset[],
): MergedAsset[] {
  const assetMap = new Map<string, TeamsAsset>();
  for (const a of assets) {
    assetMap.set(a.name, a);
  }

  return catalog.map((item) => {
    const installed = assetMap.get(item.name);
    const installedVersion = installed?.version ?? null;

    const latestNum = parseVersion(item.latestVersion);
    const installedNum = parseVersion(installedVersion);
    const hasUpdate =
      installed != null &&
      !isNaN(latestNum) &&
      !isNaN(installedNum) &&
      installedNum < latestNum;

    return {
      name: item.name,
      type: item.type,
      latestVersion: item.latestVersion,
      versionsCount: item.versionsCount,
      updatedAt: item.updatedAt,
      installedVersion,
      installed: installed != null,
      hasUpdate,
      scope: installed?.scope ?? null,
      clients: installed?.clients ?? [],
    };
  });
}

export function useTeams(): UseTeamsResult {
  const [teamsStatus, setTeamsStatus] = useState<TeamsStatus | null>(null);
  const [mergedAssets, setMergedAssets] = useState<MergedAsset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const detailCacheRef = useRef(new Map<string, AssetDetail>());
  const loadingDetailsRef = useRef(new Set<string>());
  const detailErrorsRef = useRef(new Map<string, string>());
  const [, forceUpdate] = useState(0);
  const [isInstalling, setIsInstalling] = useState(false);
  const [installError, setInstallError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/teams/status");
      if (!res.ok) throw new Error(`Status fetch failed: ${res.status}`);
      const data: TeamsStatus = await res.json();
      if (!mountedRef.current) return;
      setTeamsStatus(data);
      setMergedAssets(mergeAssets(data.catalog, data.assets));
      setError(null);
    } catch (err) {
      if (!mountedRef.current) return;
      setError((err as Error).message);
    } finally {
      if (mountedRef.current) setIsLoading(false);
    }
  }, []);

  const fetchDetail = useCallback(async (name: string) => {
    if (detailCacheRef.current.has(name) || loadingDetailsRef.current.has(name))
      return;
    loadingDetailsRef.current.add(name);
    detailErrorsRef.current.delete(name);
    forceUpdate((c) => c + 1);
    try {
      const res = await fetch(`/api/teams/detail/${encodeURIComponent(name)}`);
      if (!res.ok) throw new Error(`Detail fetch failed: ${res.status}`);
      const data: AssetDetail = await res.json();
      if (mountedRef.current) {
        detailCacheRef.current.set(name, data);
      }
    } catch (err) {
      if (mountedRef.current) {
        detailErrorsRef.current.set(name, (err as Error).message);
        console.error("Failed to fetch teams detail:", name, err);
      }
    } finally {
      loadingDetailsRef.current.delete(name);
      if (mountedRef.current) forceUpdate((c) => c + 1);
    }
  }, []);

  const installAll = useCallback(async () => {
    setIsInstalling(true);
    setInstallError(null);

    try {
      const res = await fetch("/api/teams/install", { method: "POST" });
      if (!res.ok) {
        const data = await res
          .json()
          .catch(() => ({ error: "Install failed" }));
        throw new Error(data.error || "Install failed");
      }

      let polls = 0;
      while (polls < MAX_POLLS) {
        await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
        if (!mountedRef.current) return;
        polls++;

        const statusRes = await fetch("/api/teams/status");
        if (!statusRes.ok) continue;
        const statusData: TeamsStatus = await statusRes.json();

        if (!statusData.isInstalling) {
          detailCacheRef.current.clear();
          detailErrorsRef.current.clear();
          if (mountedRef.current) {
            setTeamsStatus(statusData);
            setMergedAssets(mergeAssets(statusData.catalog, statusData.assets));
            setIsInstalling(false);
          }
          return;
        }
      }

      if (mountedRef.current) {
        setInstallError("Install taking longer than expected");
        setIsInstalling(false);
        await fetchStatus();
      }
    } catch (err) {
      if (mountedRef.current) {
        setInstallError((err as Error).message);
        setIsInstalling(false);
      }
    }
  }, [fetchStatus]);

  const initTeams = useCallback(
    async (type: string, repoUrl: string): Promise<PushResult> => {
      const res = await fetch("/api/teams/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, repoUrl }),
      });
      if (!res.ok) return { success: false, error: "Init request failed" };
      const data = await res.json();
      if (data.success) {
        fetchStatus();
      }
      return data;
    },
    [fetchStatus],
  );

  const discover = useCallback(async (): Promise<DiscoverResult> => {
    const res = await fetch("/api/teams/discover");
    if (!res.ok) return { assets: [], repoUrl: null };
    return res.json();
  }, []);

  const pushAsset = useCallback(
    async (
      asset: DiscoveredAsset,
      scope: string,
      scopeUrl: string | null,
    ): Promise<PushResult> => {
      const res = await fetch("/api/teams/push", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: asset.path,
          type: asset.type,
          name: asset.name,
          scope,
          scopeUrl,
        }),
      });
      if (!res.ok) return { success: false, error: "Push request failed" };
      return res.json();
    },
    [],
  );

  const removeAsset = useCallback(async (name: string): Promise<PushResult> => {
    const res = await fetch("/api/teams/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (!res.ok) return { success: false, error: "Remove request failed" };
    return res.json();
  }, []);

  const updateAsset = useCallback(
    async (
      name: string,
      currentVersion: string,
      scope: string,
      scopeUrl: string | null,
    ): Promise<PushResult> => {
      const res = await fetch("/api/teams/update-asset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, currentVersion, scope, scopeUrl }),
      });
      if (!res.ok) return { success: false, error: "Update request failed" };
      const data = await res.json();
      if (data.success) {
        await fetchStatus();
      }
      return data;
    },
    [fetchStatus],
  );

  useEffect(() => {
    mountedRef.current = true;
    fetchStatus();
    return () => {
      mountedRef.current = false;
    };
  }, [fetchStatus]);

  return {
    teamsStatus,
    mergedAssets,
    isLoading,
    error,
    fetchDetail,
    detailCache: detailCacheRef.current,
    loadingDetails: loadingDetailsRef.current,
    detailErrors: detailErrorsRef.current,
    installAll,
    isInstalling,
    installError,
    refresh: fetchStatus,
    discover,
    pushAsset,
    initTeams,
    removeAsset,
    updateAsset,
  };
}
