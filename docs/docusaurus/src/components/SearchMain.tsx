import React, { type ReactNode } from "react";

/** The search plugin supplies its content without a main landmark. */
export default function SearchMain({ children }: { children: ReactNode }) {
  return <main id="main-content" tabIndex={-1}>{children}</main>;
}
