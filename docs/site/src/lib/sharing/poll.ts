import { type LoadedShare, readShareUpdate } from "./sharing";

const INTERVAL = 30_000;
const MAX_BACKOFF = 5 * 60_000;
const FULL_LOOK = 15 * 60_000;
const REQUEST_TIMEOUT = 15_000;

/** One request at a time, paused when hidden; quiet polls use Redis, a full look bounds missed bumps. */
export function watchShare(id: string, key: string, receive: (state: LoadedShare) => void, problem: (message: string | null) => void = () => {}): () => void {
  let live = true;
  let finished = false;
  let running = false;
  let ready = false;
  let rev: number | undefined;
  let full = 0;
  let failures = 0;
  let blockedUntil = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let request: AbortController | undefined;
  const visible = () => document.visibilityState !== "hidden";
  const clear = () => { if (timer !== undefined) clearTimeout(timer); timer = undefined; };
  const schedule = (delay: number) => {
    clear();
    if (live && !finished && visible()) timer = setTimeout(() => void poll(), Math.max(delay, blockedUntil - Date.now()));
  };
  const poll = async () => {
    if (!live || finished || !visible() || running) return;
    if (blockedUntil > Date.now()) { schedule(blockedUntil - Date.now()); return; }
    running = true;
    request = new AbortController();
    const controller = request;
    let timedOut = false;
    const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, REQUEST_TIMEOUT);
    let delay = INTERVAL;
    try {
      const force = Date.now() - full >= FULL_LOOK;
      let update = await readShareUpdate(id, key, force ? undefined : rev, fetch, controller.signal);
      if (!live || !visible() || (controller.signal.aborted && !timedOut)) return;
      if (timedOut) update = { kind: "retry", message: "The share service could not be reached. Try again in a moment." };
      if (update.kind === "retry") {
        failures++;
        delay = Math.max(Math.min(INTERVAL * 2 ** Math.min(failures - 1, 4), MAX_BACKOFF), update.retryAfter ?? 0);
        blockedUntil = Date.now() + delay;
        if (!ready) receive({ status: "error", message: update.message });
        else problem("Updates could not be received. Showing the last version until the connection returns.");
      } else {
        failures = 0;
        blockedUntil = 0;
        problem(null);
        if (update.kind === "loaded") {
          rev = update.rev;
          full = Date.now();
          ready = update.state.status === "ready";
          receive(update.state);
          finished = !ready;
        }
      }
    } catch {
      if (live && visible() && !controller.signal.aborted) {
        failures++;
        delay = Math.min(INTERVAL * 2 ** Math.min(failures - 1, 4), MAX_BACKOFF);
        blockedUntil = Date.now() + delay;
      }
    } finally {
      clearTimeout(timeout);
      running = false;
      request = undefined;
      schedule(controller.signal.aborted && !timedOut ? 0 : delay);
    }
  };
  const visibility = () => {
    clear();
    if (!visible()) request?.abort();
    else if (!running) schedule(0);
  };
  document.addEventListener("visibilitychange", visibility);
  schedule(0);
  return () => { live = false; clear(); request?.abort(); document.removeEventListener("visibilitychange", visibility); };
}
