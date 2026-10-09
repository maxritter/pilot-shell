// What the site knows of the App's Toaster (see step-document.d.ts for why): the Copy menu says what it did in a toast.
import type { ReactNode } from "react";

export function Toaster(props: { theme?: string; position?: "bottom-center" }): ReactNode;
