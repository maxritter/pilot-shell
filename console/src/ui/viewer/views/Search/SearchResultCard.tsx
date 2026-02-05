import { Card, CardBody, Badge, Icon } from '../../components/ui';

interface SearchResult {
  id: number;
  type: 'observation' | 'summary' | 'prompt';
  title: string;
  content: string;
  project: string;
  timestamp: string;
  score: number;
  obsType?: string;
}

interface SearchResultCardProps {
  result: SearchResult;
}

const typeConfig: Record<string, { icon: string; variant: string; label: string }> = {
  observation: { icon: 'lucide:brain', variant: 'info', label: 'Observation' },
  summary: { icon: 'lucide:file-text', variant: 'warning', label: 'Summary' },
  prompt: { icon: 'lucide:message-square', variant: 'secondary', label: 'Prompt' },
  bugfix: { icon: 'lucide:bug', variant: 'error', label: 'Bug Fix' },
  feature: { icon: 'lucide:sparkles', variant: 'success', label: 'Feature' },
  refactor: { icon: 'lucide:refresh-cw', variant: 'accent', label: 'Refactor' },
  discovery: { icon: 'lucide:search', variant: 'info', label: 'Discovery' },
  decision: { icon: 'lucide:git-branch', variant: 'warning', label: 'Decision' },
  change: { icon: 'lucide:pencil', variant: 'secondary', label: 'Change' },
};

const defaultConfig = { icon: 'lucide:circle', variant: 'secondary', label: 'Unknown' };

function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return timestamp;
  }
}

export function SearchResultCard({ result }: SearchResultCardProps) {
  const displayType = result.obsType || result.type;
  const config = typeConfig[displayType] || defaultConfig;
  const scorePercent = Math.round(result.score * 100);

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-success';
    if (score >= 0.4) return 'text-warning';
    return 'text-base-content/50';
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardBody>
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-base-200 shrink-0">
            <Icon icon={config.icon} size={18} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <Badge variant={config.variant as any} size="xs">{config.label}</Badge>
              <span className="text-xs text-base-content/50">#{result.id}</span>
              {result.score > 0 && (
                <span className={`ml-auto text-xs font-mono ${getScoreColor(result.score)}`}>
                  {scorePercent}% match
                </span>
              )}
            </div>
            <h3 className="font-medium truncate">{result.title}</h3>
            <p className="text-sm text-base-content/60 mt-1 line-clamp-2">{result.content}</p>

            <div className="flex items-center gap-4 mt-3 text-xs text-base-content/50">
              {result.project && (
                <span className="flex items-center gap-1">
                  <Icon icon="lucide:folder" size={12} />
                  {result.project}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Icon icon="lucide:clock" size={12} />
                {formatTimestamp(result.timestamp)}
              </span>
            </div>
          </div>
          {result.score > 0 && (
            <div className="w-16 shrink-0 hidden sm:block">
              <div className="h-2 bg-base-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    result.score >= 0.7 ? 'bg-success' :
                    result.score >= 0.4 ? 'bg-warning' : 'bg-base-content/30'
                  }`}
                  style={{ width: `${scorePercent}%` }}
                />
              </div>
              <div className="text-[10px] text-center mt-1 text-base-content/50">similarity</div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
