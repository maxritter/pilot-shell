import type { ComponentPropsWithoutRef } from "react";

type Props = ComponentPropsWithoutRef<"a"> & {
  plan: "solo" | "team";
  billing: "monthly" | "yearly";
};

export default function CheckoutLink({ plan, billing, ...props }: Props) {
  return <a {...props} data-checkout-plan={plan} data-checkout-billing={billing} />;
}
