import { useState } from "react";
import { useCopy } from "@/hooks/useCopy";
import { INSTALL_COMMAND, WINDOWS_INSTALL_COMMAND } from "@/lib/product";

/** The install line and a copy button, with the outcome announced to screen readers. */
const InstallCommand = () => {
  const [windows, setWindows] = useState(false);
  const command = windows ? WINDOWS_INSTALL_COMMAND : INSTALL_COMMAND;
  const { copy, state, status } = useCopy(command);
  return (
    <>
      <div className="w7-install-platform" role="group" aria-label="Installation platform">
        <button type="button" aria-pressed={!windows} onClick={() => setWindows(false)}>macOS / Linux</button>
        <button type="button" aria-pressed={windows} onClick={() => setWindows(true)}>Windows · PowerShell</button>
      </div>
      <div className="w7-cmd">
        <code>{command}</code>
        <button type="button" onClick={() => void copy()} aria-label="Copy install command">
          {state === "done" ? "Copied" : state === "error" ? "Select the text" : "Copy"}
        </button>
      </div>
      {windows && <p className="w7-install-note">Native x64 and ARM64 support arrives with the next release. WSL2 remains available with the Linux command.</p>}
      <p className="w7-sr" role="status">{status}</p>
    </>
  );
};

export default InstallCommand;
