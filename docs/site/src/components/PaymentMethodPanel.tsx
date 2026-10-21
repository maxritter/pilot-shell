import { lazy, Suspense, useEffect, useState } from "react";
import { useTheme } from "@/hooks/useTheme";

const PolarPaymentMethod = lazy(async () => ({ default: (await import("@polar-sh/checkout/react/payment-method")).PolarPaymentMethod }));
const Fixture = import.meta.env.DEV ? lazy(() => import("@/dev/PaymentMethodFixture")) : null;
type Props = { token: string; fixture?: boolean; onConfirmed: () => void; onSuccess: () => void; onError: () => void };

export default function PaymentMethodPanel({ token, fixture, onConfirmed, onSuccess, onError }: Props) {
  const { theme } = useTheme();
  const [loaded, setLoaded] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  useEffect(() => {
    if (loaded) return;
    const timer = window.setTimeout(() => setTimedOut(true), 15_000);
    return () => window.clearTimeout(timer);
  }, [loaded]);
  if (timedOut) return <p role="alert">The payment form did not load. Close this dialog and try again, or contact support.</p>;
  return <div className="bl-payment-panel">{!loaded && <p role="status">Loading secure payment form…</p>}<Suspense fallback={null}>
    {Fixture && fixture ? <Fixture onLoaded={() => setLoaded(true)} onSuccess={onSuccess} /> : <PolarPaymentMethod sessionToken={token} theme={theme} locale={navigator.language} setAsDefault onLoaded={() => setLoaded(true)} onConfirmed={onConfirmed} onSuccess={onSuccess} onError={onError} />}
  </Suspense></div>;
}
