import type { MergedAsset } from "../../hooks/useTeams";

interface TeamsSummaryCardsProps {
  assets: MergedAsset[];
}

export function TeamsSummaryCards({ assets }: TeamsSummaryCardsProps) {
  const total = assets.length;
  const counts = assets.reduce(
    (acc, a) => {
      acc[a.type] = (acc[a.type] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>,
  );
  const skills = counts.skill || 0;
  const rules = counts.rule || 0;
  const commands = counts.command || 0;
  const other = total - skills - rules - commands;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="stats shadow bg-base-200">
        <div className="stat">
          <div className="stat-title">Total Assets</div>
          <div className="stat-value text-primary">{total}</div>
          <div className="stat-desc">In catalog</div>
        </div>
      </div>

      <div className="stats shadow bg-base-200">
        <div className="stat">
          <div className="stat-title">Skills</div>
          <div className="stat-value">{skills}</div>
          <div className="stat-desc">Reusable workflows</div>
        </div>
      </div>

      <div className="stats shadow bg-base-200">
        <div className="stat">
          <div className="stat-title">Rules</div>
          <div className="stat-value">{rules}</div>
          <div className="stat-desc">Coding standards</div>
        </div>
      </div>

      <div className="stats shadow bg-base-200">
        <div className="stat">
          <div className="stat-title">
            {other > 0 ? "Commands & Other" : "Commands"}
          </div>
          <div className="stat-value">{commands + other}</div>
          <div className="stat-desc">Slash commands</div>
        </div>
      </div>
    </div>
  );
}
