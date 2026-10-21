import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function PaymentMethodFixture({ onLoaded, onSuccess }: { onLoaded: () => void; onSuccess: () => void }) {
  useEffect(() => { const timer = window.setTimeout(onLoaded, 0); return () => window.clearTimeout(timer); }, [onLoaded]);
  return <div><p>Local payment-method fixture. No card details or payment are used.</p><Button onClick={async () => { await fetch("/__billing-fixture__/payment", { method: "POST" }); onSuccess(); }}>Use fixture card</Button></div>;
}
