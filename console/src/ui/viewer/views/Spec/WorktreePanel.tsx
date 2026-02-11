import { useState, useEffect, useCallback } from 'react';
import { Card, CardBody, Badge, Icon, Button, Spinner } from '../../components/ui';
import { TIMING } from '../../constants/timing';

interface WorktreeStatus {
  active: boolean;
  worktreePath: string | null;
  branch: string | null;
  baseBranch: string | null;
  planSlug: string | null;
}

interface WorktreeFileChange {
  path: string;
  status: string;
  additions: number;
  deletions: number;
}

const statusIcons: Record<string, string> = {
  A: 'lucide:file-plus',
  M: 'lucide:file-edit',
  D: 'lucide:file-minus',
};

const statusColors: Record<string, string> = {
  A: 'text-success',
  M: 'text-warning',
  D: 'text-error',
};

export function WorktreePanel() {
  const [status, setStatus] = useState<WorktreeStatus | null>(null);
  const [files, setFiles] = useState<WorktreeFileChange[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isDiscarding, setIsDiscarding] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    try {
      const res = await fetch('/api/worktree/status');
      const data = await res.json();
      setStatus(data);

      if (data.active) {
        const diffRes = await fetch('/api/worktree/diff');
        const diffData = await diffRes.json();
        setFiles(diffData.files || []);
      } else {
        setFiles([]);
      }
    } catch {
      setStatus(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, TIMING.SPEC_REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadStatus]);

  const handleSync = async () => {
    if (!confirm('Sync worktree changes to the base branch via squash merge?')) return;
    setIsSyncing(true);
    setSyncResult(null);
    try {
      const res = await fetch('/api/worktree/sync', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSyncResult(`Synced ${data.files_changed} files — commit ${data.commit_hash?.slice(0, 7)}`);
        await loadStatus();
      } else {
        setSyncResult(`Sync failed: ${data.error}`);
      }
    } catch (err) {
      setSyncResult('Sync failed');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDiscard = async () => {
    if (!confirm('Discard all worktree changes? This cannot be undone.')) return;
    setIsDiscarding(true);
    setSyncResult(null);
    try {
      const res = await fetch('/api/worktree/discard', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSyncResult('Worktree discarded');
        await loadStatus();
      } else {
        setSyncResult(`Discard failed: ${data.error}`);
      }
    } catch {
      setSyncResult('Discard failed');
    } finally {
      setIsDiscarding(false);
    }
  };

  if (isLoading) return null;
  if (!status?.active) return null;

  const totalAdditions = files.reduce((sum, f) => sum + f.additions, 0);
  const totalDeletions = files.reduce((sum, f) => sum + f.deletions, 0);

  return (
    <Card>
      <CardBody className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Icon icon="lucide:git-branch" size={16} className="text-primary" />
            <span className="text-sm font-medium">Worktree Isolation</span>
            <Badge variant="info" size="xs">{status.branch}</Badge>
          </div>
          <div className="flex items-center gap-1.5">
            <Button
              variant="primary"
              size="xs"
              onClick={handleSync}
              disabled={isSyncing || isDiscarding || files.length === 0}
            >
              {isSyncing ? <Spinner size="xs" /> : <Icon icon="lucide:git-merge" size={12} />}
              <span className="ml-1">Sync</span>
            </Button>
            <Button
              variant="ghost"
              size="xs"
              onClick={handleDiscard}
              disabled={isSyncing || isDiscarding}
            >
              {isDiscarding ? <Spinner size="xs" /> : <Icon icon="lucide:trash-2" size={12} className="text-error" />}
              <span className="ml-1">Discard</span>
            </Button>
          </div>
        </div>

        {/* Diff summary */}
        <div className="flex items-center gap-3 text-xs text-base-content/60 mb-2">
          <span>{files.length} file{files.length !== 1 ? 's' : ''} changed</span>
          {totalAdditions > 0 && <span className="text-success">+{totalAdditions}</span>}
          {totalDeletions > 0 && <span className="text-error">-{totalDeletions}</span>}
          <span className="ml-auto">
            base: <span className="font-mono text-base-content/80">{status.baseBranch}</span>
          </span>
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div className="space-y-0.5 max-h-40 overflow-y-auto">
            {files.map((file) => (
              <div key={file.path} className="flex items-center gap-2 text-xs py-0.5">
                <Icon
                  icon={statusIcons[file.status] || 'lucide:file'}
                  size={12}
                  className={statusColors[file.status] || 'text-base-content/50'}
                />
                <span className="font-mono text-base-content/80 truncate">{file.path}</span>
                <span className="ml-auto flex items-center gap-1 flex-shrink-0">
                  {file.additions > 0 && <span className="text-success">+{file.additions}</span>}
                  {file.deletions > 0 && <span className="text-error">-{file.deletions}</span>}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Sync result message */}
        {syncResult && (
          <div className={`mt-2 text-xs px-2 py-1 rounded ${
            syncResult.includes('failed') ? 'bg-error/10 text-error' : 'bg-success/10 text-success'
          }`}>
            {syncResult}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
