import { useCopy } from "@/hooks/useCopy";
import { INSTALL_COMMAND } from "@/lib/product";

/** The install line and a copy button, with the outcome announced to screen readers. */
const InstallCommand = () => {
  const { copy, state, status } = useCopy(INSTALL_COMMAND);
  return (
    <>
      <div className="w7-cmd">
        <code>{INSTALL_COMMAND}</code>
        <button type="button" onClick={() => void copy()} aria-label="Copy install command">
          {state === "done" ? "Copied" : state === "error" ? "Select the text" : "Copy"}
        </button>
      </div>
      <p className="w7-sr" role="status">{status}</p>
    </>
  );
};

export default InstallCommand;
