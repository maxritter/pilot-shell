import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface IconTileProps {
  icon: LucideIcon;
  /** Tailwind size classes for the tile square, e.g. "w-10 h-10". */
  sizeClass?: string;
  /** Tailwind size classes for the icon, e.g. "h-5 w-5". */
  iconClass?: string;
  /** "team" switches to the indigo Team-plan accent. */
  color?: "primary" | "team";
  /** Background strength: 10 or 20 (alpha percent). */
  strength?: 10 | 15 | 20;
  className?: string;
}

/** Signature Pilot Shell motif: rounded-xl square wash with a lucide icon. */
const IconTile = ({
  icon: Icon,
  sizeClass = "w-10 h-10",
  iconClass = "h-5 w-5",
  color = "primary",
  strength = 10,
  className,
}: IconTileProps) => {
  const bg =
    color === "team"
      ? { 10: "bg-indigo-500/10", 15: "bg-indigo-500/15", 20: "bg-indigo-500/20" }[strength]
      : { 10: "bg-primary/10", 15: "bg-primary/15", 20: "bg-primary/20" }[strength];
  const fg = color === "team" ? "text-indigo-500" : "text-primary";

  return (
    <div
      className={cn(
        "rounded-xl flex items-center justify-center flex-shrink-0",
        sizeClass,
        bg,
        className,
      )}
      aria-hidden="true"
    >
      <Icon className={cn(iconClass, fg)} />
    </div>
  );
};

export default IconTile;
