import { useEffect } from "react";
import { Check, Building2, Sparkles, Calendar, Mail, Shield } from "lucide-react";
import { PolarEmbedCheckout } from "@polar-sh/checkout/embed";
import { Button } from "@/components/ui/button";
import { useInView } from "@/hooks/use-in-view";

const SOLO_CHECKOUT_URL =
  import.meta.env.VITE_POLAR_CHECKOUT_SOLO ||
  "https://buy.polar.sh/polar_cl_nxoqkuI0m3K60V4EpyaruDdPsd7CjS4jalKqc4TszL3";
const TEAM_CHECKOUT_URL =
  import.meta.env.VITE_POLAR_CHECKOUT_TEAM ||
  "https://buy.polar.sh/polar_cl_y5uSffkVLnESyfzfOSJ1M9YmMd8sIpcT7bza82oFv4C";
const ENTERPRISE_FORM_URL = "https://form.typeform.com/to/J7h2jjfw";
const PORTAL_URL =
  import.meta.env.VITE_POLAR_PORTAL_URL || "https://polar.sh/max-ritter/portal";
const IS_PRODUCTION =
  import.meta.env.PROD &&
  !import.meta.env.VITE_POLAR_PORTAL_URL?.includes("sandbox");

const PricingSection = () => {
  const [headerRef, headerInView] = useInView<HTMLDivElement>();
  const [cardsRef, cardsInView] = useInView<HTMLDivElement>();

  const soloUrl = SOLO_CHECKOUT_URL;
  const teamUrl = TEAM_CHECKOUT_URL;

  useEffect(() => {
    if (IS_PRODUCTION) {
      PolarEmbedCheckout.init();
    }
  }, []);

  return (
    <section
      id="pricing"
      className="py-16 lg:py-24 px-4 sm:px-6 relative"
      aria-labelledby="pricing-heading"
    >
      <div className="max-w-6xl mx-auto">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        {/* Header */}
        <div
          ref={headerRef}
          className={`text-center mb-16 ${headerInView ? "animate-fade-in-up" : "opacity-0"}`}
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
            Pricing
          </h2>
          <p className="text-muted-foreground text-lg sm:text-xl max-w-3xl mx-auto">
            Get instant access to <span className="text-foreground font-medium">best practices</span> from daily production usage — a <span className="text-foreground font-medium">shortcut</span> to <span className="text-foreground font-medium">state-of-the-art</span> Claude Code development.
            A <span className="text-foreground font-medium">free 7-day trial</span> starts automatically on install — full features, no subscription required.
          </p>
        </div>

        <div ref={cardsRef} className="grid md:grid-cols-3 gap-6 sm:gap-8">
          {/* Solo - Featured */}
          <div
            className={`group relative rounded-lg p-4 sm:p-6 md:p-8 border-2 border-primary/50 bg-card
              hover:border-primary hover:bg-card hover:border-primary
              transition-all duration-300 scale-[1.02]
              ${cardsInView ? "animate-fade-in-up animation-delay-0" : "opacity-0"}`}
          >
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary to-transparent" />
            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center
                group-hover:bg-primary/30 group-hover:scale-110 transition-all duration-300"
              >
                <Check className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-foreground">Solo</h3>
                <p className="text-xs text-muted-foreground">1 developer</p>
              </div>
            </div>

            <div className="mb-6">
              <span className="text-4xl font-bold text-foreground">$14</span>
              <span className="text-muted-foreground">/month</span>
            </div>

            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Rules, hooks, standards, LSPs, MCPs
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Spec-driven mode, memory system, browser dashboard
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Pilot Bot — 24/7 automation agent with scheduled jobs
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Cross-machine skill sync — push/pull skills across all your machines
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Community support via GitHub Issues
                </span>
              </li>
            </ul>

            <Button asChild className="w-full">
              <a
                href={soloUrl}
                {...(IS_PRODUCTION
                  ? {
                      "data-polar-checkout": true,
                      "data-polar-checkout-theme": "dark",
                    }
                  : { target: "_blank", rel: "noopener" })}
              >
                Subscribe
              </a>
            </Button>
          </div>

          {/* Team */}
          <div
            className={`group relative rounded-lg p-4 sm:p-6 md:p-8 border border-border/50 bg-card
              hover:border-indigo-500/50 hover:bg-card hover:border-indigo-500/50
              transition-all duration-300
              ${cardsInView ? "animate-fade-in-up animation-delay-100" : "opacity-0"}`}
          >
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500 to-transparent" />
            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-12 h-12 bg-indigo-500/15 rounded-xl flex items-center justify-center
                group-hover:bg-indigo-500/25 group-hover:scale-110 transition-all duration-300"
              >
                <Building2 className="h-6 w-6 text-indigo-500" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-foreground">Team</h3>
                <p className="text-xs text-muted-foreground">Multiple developers</p>
              </div>
            </div>

            <div className="mb-6">
              <span className="text-4xl font-bold text-foreground">$35</span>
              <span className="text-muted-foreground">/seat/month</span>
            </div>

            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Everything in Solo
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Extension sharing — share skills, rules, commands, and agents via git
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Customization packs — override workflows, skills, and rules via git
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Seat management — assign and manage all seats for your team in the portal
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Priority support — direct support on issues and feature requests
                </span>
              </li>
            </ul>

            <Button
              asChild
              variant="outline"
              className="w-full border-indigo-500/50 hover:bg-indigo-500/10"
            >
              <a href={teamUrl} target="_blank" rel="noopener">
                Subscribe
              </a>
            </Button>
          </div>

          {/* Enterprise */}
          <div
            className={`group relative rounded-lg p-4 sm:p-6 md:p-8 border border-border/50 bg-card
              hover:border-amber-500/50 hover:bg-card hover:border-amber-500/50
              transition-all duration-300
              ${cardsInView ? "animate-fade-in-up animation-delay-200" : "opacity-0"}`}
          >
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent" />
            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-12 h-12 bg-amber-500/15 rounded-xl flex items-center justify-center
                group-hover:bg-amber-500/25 group-hover:scale-110 transition-all duration-300"
              >
                <Shield className="h-6 w-6 text-amber-500" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-foreground">Enterprise</h3>
                <p className="text-xs text-muted-foreground">100+ seats</p>
              </div>
            </div>

            <div className="mb-6">
              <span className="text-2xl font-bold text-foreground">Custom</span>
              <span className="text-muted-foreground text-sm ml-1">pricing</span>
            </div>

            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Everything in Team
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Full source code access — launcher, console, and all closed-source components
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Fork and modify — full control to customize every part for your organization
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
                <span className="text-muted-foreground text-sm group-hover:text-foreground/80 transition-colors">
                  Dedicated onboarding, ongoing updates, and priority support
                </span>
              </li>
            </ul>

            <Button
              asChild
              variant="outline"
              className="w-full border-amber-500/50 hover:bg-amber-500/10"
            >
              <a href={ENTERPRISE_FORM_URL} target="_blank" rel="noopener">
                Apply for Enterprise
              </a>
            </Button>
          </div>
        </div>

        <p className="text-center text-sm text-muted-foreground mt-6">
          All plans work across multiple personal machines — one subscription,
          all your devices.
        </p>
        <p className="text-center text-sm text-muted-foreground mt-2">
          Already a subscriber?{" "}
          <a href={PORTAL_URL} className="text-primary hover:underline">
            Manage your subscription
          </a>
        </p>

        {/* Rolling out for your team */}
        <div className="mt-16 text-center max-w-3xl mx-auto">
          <h3 className="text-2xl sm:text-3xl font-bold text-foreground mb-3">
            Rolling Out for Your Team?
          </h3>
          <p className="text-muted-foreground text-base sm:text-lg mb-6">
            I'd love to help figure out if Pilot Shell is the right fit for your team and get everyone set up.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button size="lg" asChild>
              <a
                href="https://calendly.com/rittermax/pilot-shell"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Calendar className="mr-2 h-4 w-4" />
                Book a Call
              </a>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <a href="mailto:mail@maxritter.net">
                <Mail className="mr-2 h-4 w-4" />
                Send a Message
              </a>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
