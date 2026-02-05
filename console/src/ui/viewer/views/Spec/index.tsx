import { useState, useEffect, useCallback } from 'react';
import { Card, CardBody, Badge, Icon, Spinner, Progress } from '../../components/ui';
import { SpecContent } from './SpecContent';

interface PlanInfo {
  name: string;
  status: 'PENDING' | 'COMPLETE' | 'VERIFIED';
  completed: number;
  total: number;
  phase: 'plan' | 'implement' | 'verify';
  iterations: number;
  approved: boolean;
  filePath: string;
  modifiedAt: string;
}

interface PlanContent {
  content: string;
  name: string;
  status: string;
  filePath: string;
}

interface ParsedTask {
  number: number;
  title: string;
  completed: boolean;
}

interface ParsedPlan {
  title: string;
  goal: string;
  tasks: ParsedTask[];
  implementationSection: string;
}

const statusConfig = {
  PENDING: { color: 'warning', icon: 'lucide:clock', label: 'In Progress' },
  COMPLETE: { color: 'info', icon: 'lucide:check-circle', label: 'Complete' },
  VERIFIED: { color: 'success', icon: 'lucide:shield-check', label: 'Verified' },
} as const;

function parsePlanContent(content: string): ParsedPlan {
  const titleMatch = content.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].replace(' Implementation Plan', '') : 'Untitled';

  const goalMatch = content.match(/\*\*Goal:\*\*\s*(.+?)(?:\n|$)/);
  const goal = goalMatch ? goalMatch[1] : '';

  const tasks: ParsedTask[] = [];
  const taskRegex = /^- \[(x| )\] Task (\d+):\s*(.+)$/gm;
  let match;
  while ((match = taskRegex.exec(content)) !== null) {
    tasks.push({
      number: parseInt(match[2], 10),
      title: match[3],
      completed: match[1] === 'x',
    });
  }

  const implMatch = content.match(/## Implementation Tasks\n([\s\S]*?)(?=\n## [^#]|$)/);
  const implementationSection = implMatch ? implMatch[1].trim() : '';

  return { title, goal, tasks, implementationSection };
}

export function SpecView() {
  const [specs, setSpecs] = useState<PlanInfo[]>([]);
  const [selectedSpec, setSelectedSpec] = useState<string | null>(null);
  const [content, setContent] = useState<PlanContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSpecs = useCallback(async () => {
    try {
      const res = await fetch('/api/plans/active');
      const data = await res.json();
      setSpecs(data.specs || []);

      if (data.specs?.length > 0 && !selectedSpec) {
        setSelectedSpec(data.specs[0].filePath);
      }
    } catch (err) {
      setError('Failed to load specs');
      console.error('Failed to load specs:', err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedSpec]);

  const loadContent = useCallback(async (filePath: string) => {
    setIsLoadingContent(true);
    setError(null);
    try {
      const res = await fetch(`/api/plan/content?path=${encodeURIComponent(filePath)}`);
      if (!res.ok) {
        throw new Error('Failed to load spec content');
      }
      const data = await res.json();
      setContent(data);
    } catch (err) {
      setError('Failed to load spec content');
      console.error('Failed to load spec content:', err);
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  useEffect(() => {
    loadSpecs();
  }, [loadSpecs]);

  useEffect(() => {
    if (selectedSpec) {
      loadContent(selectedSpec);
    }
  }, [selectedSpec, loadContent]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (specs.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Spec Viewer</h1>
          <p className="text-base-content/60">View active spec-driven development plans</p>
        </div>

        <Card>
          <CardBody>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Icon icon="lucide:file-text" size={48} className="text-base-content/30 mb-4" />
              <h3 className="text-lg font-medium mb-2">No Active Specs</h3>
              <p className="text-base-content/60 max-w-md">
                Use <code className="text-primary bg-base-300 px-1 rounded">/spec</code> in Claude Pilot to start a spec-driven development workflow.
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  const currentSpec = specs.find(s => s.filePath === selectedSpec);
  const config = currentSpec ? statusConfig[currentSpec.status] : null;
  const parsed = content ? parsePlanContent(content.content) : null;
  const completedCount = parsed?.tasks.filter(t => t.completed).length || 0;
  const totalCount = parsed?.tasks.length || 0;
  const progressPct = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header with spec selector */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Spec Viewer</h1>
          <p className="text-base-content/60">View active spec-driven development plans</p>
        </div>

        {specs.length > 1 && (
          <select
            className="select select-bordered select-sm"
            value={selectedSpec || ''}
            onChange={(e) => setSelectedSpec(e.target.value)}
          >
            {specs.map((spec) => (
              <option key={spec.filePath} value={spec.filePath}>
                {spec.name} ({spec.status})
              </option>
            ))}
          </select>
        )}
      </div>

      {isLoadingContent ? (
        <div className="flex items-center justify-center py-12">
          <Spinner size="md" />
        </div>
      ) : error ? (
        <Card>
          <CardBody>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Icon icon="lucide:alert-circle" size={48} className="text-error mb-4" />
              <p className="text-error">{error}</p>
            </div>
          </CardBody>
        </Card>
      ) : parsed ? (
        <>
          {/* Structured Header Card */}
          <Card>
            <CardBody className="p-5">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold">{parsed.title}</h2>
                  {parsed.goal && (
                    <p className="text-base-content/60 text-sm mt-1">{parsed.goal}</p>
                  )}
                </div>
                {config && (
                  <Badge variant={config.color as 'warning' | 'info' | 'success'} size="sm" className="whitespace-nowrap">
                    <Icon icon={config.icon} size={12} className="mr-1" />
                    {config.label}
                  </Badge>
                )}
              </div>

              {/* Progress bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-base-content/70">Progress</span>
                  <span className="font-medium">{completedCount} / {totalCount} tasks</span>
                </div>
                <Progress value={progressPct} max={100} variant="primary" />
              </div>

              {/* Task Checklist */}
              <div className="space-y-2">
                {parsed.tasks.map((task) => (
                  <div
                    key={task.number}
                    className={`flex items-center gap-3 p-2 rounded-lg ${
                      task.completed ? 'bg-success/10' : 'bg-base-200/50'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center ${
                      task.completed ? 'bg-success text-success-content' : 'bg-base-300'
                    }`}>
                      {task.completed ? (
                        <Icon icon="lucide:check" size={14} />
                      ) : (
                        <span className="text-xs text-base-content/50">{task.number}</span>
                      )}
                    </div>
                    <span className={`text-sm ${task.completed ? 'text-base-content/70' : 'text-base-content'}`}>
                      Task {task.number}: {task.title}
                    </span>
                  </div>
                ))}
              </div>

              {/* Metadata row */}
              {currentSpec && (
                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-base-300/50 text-xs text-base-content/50">
                  {currentSpec.iterations > 0 && (
                    <div className="flex items-center gap-1">
                      <Icon icon="lucide:repeat" size={12} />
                      <span>{currentSpec.iterations} iteration{currentSpec.iterations > 1 ? 's' : ''}</span>
                    </div>
                  )}
                  {!currentSpec.approved && currentSpec.status === 'PENDING' && (
                    <Badge variant="warning" size="xs">Awaiting Approval</Badge>
                  )}
                  <div className="flex items-center gap-1 ml-auto">
                    <Icon icon="lucide:file" size={12} />
                    <span className="font-mono">{currentSpec.filePath.split('/').pop()}</span>
                  </div>
                </div>
              )}
            </CardBody>
          </Card>

          {/* Implementation Tasks - Markdown */}
          {parsed.implementationSection && (
            <Card>
              <CardBody className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Icon icon="lucide:list-tree" size={18} />
                  Implementation Details
                </h3>
                <SpecContent content={parsed.implementationSection} />
              </CardBody>
            </Card>
          )}
        </>
      ) : null}
    </div>
  );
}
