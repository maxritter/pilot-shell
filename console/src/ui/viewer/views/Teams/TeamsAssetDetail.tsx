import type { AssetDetail } from "../../hooks/useTeams";

interface TeamsAssetDetailProps {
  detail: AssetDetail | null;
  isLoading: boolean;
  onRetry?: () => void;
}

export function TeamsAssetDetail({
  detail,
  isLoading,
  onRetry,
}: TeamsAssetDetailProps) {
  if (isLoading) {
    return (
      <div className="p-4 bg-base-200 rounded-b-lg flex items-center gap-2">
        <span className="loading loading-spinner loading-sm" />
        <span className="text-sm text-base-content/60">Loading details...</span>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="p-4 bg-base-200 rounded-b-lg text-sm text-base-content/60">
        <span>Failed to load details.</span>
        {onRetry && (
          <button className="btn btn-ghost btn-xs ml-2" onClick={onRetry}>
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="p-4 bg-base-200 rounded-b-lg space-y-3">
      {detail.metadata.description && (
        <p className="text-sm text-base-content/70">
          {detail.metadata.description}
        </p>
      )}

      {detail.versions.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-base-content/50 uppercase mb-2">
            Version History
          </h4>
          <table className="table table-xs w-full">
            <thead>
              <tr>
                <th>Version</th>
                <th>Date</th>
                <th>Files</th>
              </tr>
            </thead>
            <tbody>
              {detail.versions.map((v) => (
                <tr key={v.version}>
                  <td className="font-mono">v{v.version}</td>
                  <td className="text-base-content/60">
                    {v.createdAt ?? "\u2014"}
                  </td>
                  <td>{v.filesCount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {detail.metadata.authors.length > 0 && (
        <div className="text-xs text-base-content/50">
          Authors: {detail.metadata.authors.join(", ")}
        </div>
      )}
    </div>
  );
}
