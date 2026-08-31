import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionHeaderProps {
  kicker?: string;
  title: string;
  titleId?: string;
  lead?: ReactNode;
  className?: string;
}

/** Centered section header: mono uppercase kicker, bold title, muted lead. */
const SectionHeader = ({ kicker, title, titleId, lead, className }: SectionHeaderProps) => (
  <div className={cn("text-center max-w-3xl mx-auto", className)}>
    {kicker && (
      <div className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-primary mb-3">
        {kicker}
      </div>
    )}
    <h2
      id={titleId}
      className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-foreground"
    >
      {title}
    </h2>
    {lead && (
      <p className="text-muted-foreground text-base sm:text-lg leading-relaxed mt-3.5">
        {lead}
      </p>
    )}
  </div>
);

export default SectionHeader;
