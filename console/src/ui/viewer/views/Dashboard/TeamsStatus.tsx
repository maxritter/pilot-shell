import { Card, CardBody, CardTitle, Badge, Icon } from "../../components/ui";

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
}

interface TeamsStatusProps {
  installed: boolean;
  version: string | null;
  configured: boolean;
  repoUrl: string | null;
  profile: string | null;
  assets: TeamsAsset[];
  catalog: TeamsCatalogItem[];
  isInstalling: boolean;
  isLoading?: boolean;
}

function formatRepoUrl(url: string): string {
  try {
    const u = new URL(url);
    return (u.host + u.pathname).replace(/\.git$/, "");
  } catch {
    return url;
  }
}

export function TeamsStatus(props: TeamsStatusProps) {
  const {
    installed,
    version,
    configured,
    repoUrl,
    assets,
    catalog,
    isLoading,
  } = props;

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <CardTitle>Teams</CardTitle>
            <Badge variant="ghost">Loading...</Badge>
          </div>
          <div className="space-y-3 animate-pulse">
            <div className="h-4 bg-base-300 rounded w-3/4"></div>
            <div className="h-4 bg-base-300 rounded w-1/2"></div>
          </div>
        </CardBody>
      </Card>
    );
  }

  const installedNames = new Set(assets.map((a) => a.name));
  const availableCount = catalog.filter(
    (c) => !installedNames.has(c.name),
  ).length;

  if (!installed) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <CardTitle>Teams</CardTitle>
            <Badge variant="ghost">Not Installed</Badge>
          </div>
          <div className="text-sm text-base-content/60">
            <p>
              sx is not installed. Run the Pilot installer to set up team
              sharing.
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (!configured) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CardTitle>Teams</CardTitle>
              {version && (
                <Badge variant="ghost" size="sm">
                  v{version}
                </Badge>
              )}
            </div>
            <Badge variant="warning">Not Configured</Badge>
          </div>
          <div className="text-sm text-base-content/60">
            <p>
              sx is installed but no repository is configured. Open the{" "}
              <a href="#/teams" className="text-primary hover:underline">
                Teams page
              </a>{" "}
              to set up.
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody className="flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CardTitle>Teams</CardTitle>
            <Badge variant="ghost" size="sm">
              Workspace
            </Badge>
          </div>
          <Badge variant="success">Connected</Badge>
        </div>

        <div className="space-y-3 flex-1">
          {repoUrl && (
            <div className="flex items-center gap-2 text-sm">
              <Icon
                icon="lucide:git-branch"
                size={16}
                className="text-base-content/50"
              />
              <span className="text-base-content/70">Repository:</span>
              <span className="font-mono text-xs truncate">
                {formatRepoUrl(repoUrl)}
              </span>
            </div>
          )}

          <div className="flex items-center gap-2 text-sm">
            <Icon
              icon="lucide:package"
              size={16}
              className="text-base-content/50"
            />
            <span className="text-base-content/70">Installed:</span>
            <span className="font-semibold">{assets.length}</span>
            {availableCount > 0 && (
              <span className="text-base-content/40">
                ({availableCount} available)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 text-sm">
            <Icon
              icon="lucide:cloud"
              size={16}
              className="text-base-content/50"
            />
            <span className="text-base-content/70">In catalog:</span>
            <span className="font-semibold">{catalog.length}</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
