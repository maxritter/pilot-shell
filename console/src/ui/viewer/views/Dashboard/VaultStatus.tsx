import { Card, CardBody, CardTitle, Badge, Icon } from '../../components/ui';

interface VaultAsset {
  name: string;
  version: string;
  type: string;
  clients: string[];
  status: string;
  scope: string;
}

interface VaultCatalogItem {
  name: string;
  type: string;
  latestVersion: string;
  versionsCount: number;
}

interface VaultStatusProps {
  installed: boolean;
  version: string | null;
  configured: boolean;
  vaultUrl: string | null;
  profile: string | null;
  assets: VaultAsset[];
  catalog: VaultCatalogItem[];
  isInstalling: boolean;
  isLoading?: boolean;
}

const TYPE_ICONS: Record<string, string> = {
  skill: 'lucide:cpu',
  rule: 'lucide:scroll-text',
  command: 'lucide:terminal',
  agent: 'lucide:bot',
  hook: 'lucide:webhook',
  mcp: 'lucide:plug',
};

function formatVaultUrl(url: string): string {
  try {
    const u = new URL(url);
    return (u.host + u.pathname).replace(/\.git$/, '');
  } catch {
    return url;
  }
}

export function VaultStatus(props: VaultStatusProps) {
  const { installed, version, configured, vaultUrl, assets, catalog, isLoading } = props;

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <CardTitle>Team Vault</CardTitle>
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

  const installedNames = new Set(assets.map(a => a.name));
  const availableCount = catalog.filter(c => !installedNames.has(c.name)).length;

  if (!installed) {
    return (
      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <CardTitle>Team Vault</CardTitle>
            <Badge variant="ghost">Not Installed</Badge>
          </div>
          <div className="text-sm text-base-content/60">
            <p>sx is not installed. Run the Pilot installer or install from <span className="font-mono text-primary">skills.new</span>.</p>
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
              <CardTitle>Team Vault</CardTitle>
              {version && <Badge variant="ghost" size="sm">v{version}</Badge>}
            </div>
            <Badge variant="warning">Not Configured</Badge>
          </div>
          <div className="text-sm text-base-content/60">
            <p>sx is installed but no vault is configured. Run <span className="font-mono text-primary">/vault</span> to set up.</p>
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
            <CardTitle>Team Vault</CardTitle>
            <Badge variant="ghost" size="sm">Workspace</Badge>
          </div>
          <Badge variant="success">Connected</Badge>
        </div>

        <div className="space-y-3 flex-1">
          {/* Vault URL */}
          {vaultUrl && (
            <div className="flex items-center gap-2 text-sm">
              <Icon icon="lucide:git-branch" size={16} className="text-base-content/50" />
              <span className="text-base-content/70">Vault:</span>
              <span className="font-mono text-xs truncate">{formatVaultUrl(vaultUrl)}</span>
            </div>
          )}

          {/* Counts */}
          <div className="flex items-center gap-2 text-sm">
            <Icon icon="lucide:package" size={16} className="text-base-content/50" />
            <span className="text-base-content/70">Installed:</span>
            <span className="font-semibold">{assets.length}</span>
            {availableCount > 0 && (
              <span className="text-base-content/40">
                ({availableCount} available)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 text-sm">
            <Icon icon="lucide:cloud" size={16} className="text-base-content/50" />
            <span className="text-base-content/70">In vault:</span>
            <span className="font-semibold">{catalog.length}</span>
          </div>

          {/* Installed assets list */}
          {assets.length > 0 && (
            <div className="pt-2 space-y-1.5">
              {assets.map((asset) => (
                <div key={`${asset.scope}-${asset.name}`} className="flex items-center gap-2 text-xs">
                  <Icon
                    icon={TYPE_ICONS[asset.type] || 'lucide:file'}
                    size={14}
                    className="text-primary/70"
                  />
                  <span className="font-mono font-medium">{asset.name}</span>
                  <span className="text-base-content/40">v{asset.version}</span>
                  <Badge
                    variant={asset.scope === 'Global' ? 'ghost' : 'info'}
                    size="xs"
                  >
                    {asset.scope === 'Global' ? 'global' : 'project'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
