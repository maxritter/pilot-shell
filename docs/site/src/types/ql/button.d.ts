// What the site knows of the App's shadcn Button (see step-document.d.ts for why). The App's look is the point:
// a button beside the Reader's Sections and Copy is drawn by the same component.
import type { ComponentProps, ReactNode } from "react";

export type ButtonProps = ComponentProps<"button"> & {
  variant?: "default" | "outline" | "secondary" | "ghost" | "destructive" | "link";
  size?: "default" | "xs" | "sm" | "lg" | "icon" | "icon-xs" | "icon-sm" | "icon-lg";
  asChild?: boolean;
};

export function Button(props: ButtonProps): ReactNode;
