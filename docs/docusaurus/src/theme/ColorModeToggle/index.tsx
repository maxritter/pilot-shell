import React from "react";
import clsx from "clsx";
import useIsBrowser from "@docusaurus/useIsBrowser";
import { useColorMode } from "@docusaurus/theme-common";
import IconLightMode from "@theme/Icon/LightMode";
import IconDarkMode from "@theme/Icon/DarkMode";
import type { Props } from "@theme/ColorModeToggle";

export default function ColorModeToggle({ className, buttonClassName, onChange }: Props) {
  const { colorMode } = useColorMode();
  const isBrowser = useIsBrowser();
  const next = colorMode === "dark" ? "light" : "dark";
  return (
    <div className={className}>
      <button
        type="button"
        className={clsx("clean-btn ql-theme-toggle", buttonClassName)}
        disabled={!isBrowser}
        aria-label={`Switch to ${next}`}
        title={`Switch to ${next}`}
        onClick={() => onChange(next)}
      >
        <IconLightMode aria-hidden className="ql-light-icon" />
        <IconDarkMode aria-hidden className="ql-dark-icon" />
      </button>
    </div>
  );
}
