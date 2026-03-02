import { Icon } from "./ui";

interface TeamGateProps {
  tier: string | null;
  featureName: string;
  children?: React.ReactNode;
}

export function TeamGate({ tier, featureName, children }: TeamGateProps) {
  if (tier === "team") {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      <div className="opacity-30 pointer-events-none blur-[2px] select-none">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="card bg-base-100 shadow-xl max-w-sm text-center">
          <div className="card-body items-center gap-4 py-8">
            <div className="w-14 h-14 bg-base-200 rounded-full flex items-center justify-center">
              <Icon
                icon="lucide:lock"
                size={24}
                className="text-base-content/50"
              />
            </div>
            <h3 className="card-title text-lg">Team Plan Required</h3>
            <p className="text-sm text-base-content/60">
              {featureName} is available on the Team plan. Upgrade to share
              assets, configure repositories, and collaborate with your team.
            </p>
            <a
              href="https://pilot-shell.com/#pricing"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary btn-sm mt-2"
            >
              <Icon icon="lucide:arrow-up-right" size={14} />
              Upgrade to Team
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
