import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  CircleUserRound,
  Github,
  Linkedin,
  Mail,
  ScrollText,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Logo from "./Logo";
import { navigateToSection } from "@/utils/navigateToSection";
import { useInView } from "@/hooks/use-in-view";
import { PORTAL_URL } from "@/lib/links";

const Footer = () => {
  const [footerRef, footerInView] = useInView<HTMLElement>();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <footer
      ref={footerRef}
      className={`py-16 px-6 bg-background border-t border-border ${footerInView ? "animate-fade-in-up" : "opacity-0"}`}
      role="contentinfo"
    >
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 mb-12">
          <div className="flex flex-col gap-3">
            <Logo variant="footer" />
            <p className="text-sm text-muted-foreground max-w-xs">
              How real engineers run Claude Code and Codex
            </p>
          </div>

          <nav className="flex flex-col gap-3" aria-label="Footer navigation">
            <h3 className="text-sm font-medium">Quick Links</h3>
            <ul>
              <li>
                <button
                  onClick={() =>
                    navigateToSection(
                      "installation",
                      location.pathname,
                      navigate,
                    )
                  }
                  className="inline-flex min-h-11 items-center text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  Getting Started
                </button>
              </li>
              <li>
                <button
                  onClick={() =>
                    navigateToSection("features", location.pathname, navigate)
                  }
                  className="inline-flex min-h-11 items-center text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  Features
                </button>
              </li>
              <li>
                <a
                  href="/docs"
                  className="inline-flex min-h-11 items-center text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  Docs
                </a>
              </li>
              <li>
                <Link
                  to="/pricing"
                  className="inline-flex min-h-11 items-center text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  Subscribe
                </Link>
              </li>
              <li>
                <a
                  href={PORTAL_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex min-h-11 items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  <CircleUserRound className="h-3.5 w-3.5" />
                  Manage Subscription
                </a>
              </li>
              <li>
                <button
                  onClick={() =>
                    navigateToSection("faq", location.pathname, navigate)
                  }
                  className="inline-flex min-h-11 items-center text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  FAQ
                </button>
              </li>
              <li>
                <a
                  href="https://github.com/maxritter/pilot-shell/releases"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex min-h-11 items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  <ScrollText className="h-3.5 w-3.5" />
                  Changelog
                </a>
              </li>
            </ul>
          </nav>

          <div className="flex flex-col items-start gap-4">
            <h3 className="text-sm font-medium">Connect</h3>
            <p className="text-xs text-muted-foreground">
              Follow on LinkedIn for updates
            </p>
            <nav className="flex gap-3" aria-label="Social media links">
              <Button
                size="icon"
                variant="outline"
                className="h-11 w-11 border-primary/50 transition-colors hover:border-primary hover:bg-primary/10"
                asChild
              >
                <a
                  href="https://github.com/maxritter/pilot-shell"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="GitHub"
                >
                  <Github className="h-5 w-5" />
                </a>
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="h-11 w-11 border-primary/50 transition-colors hover:border-primary hover:bg-primary/10"
                asChild
              >
                <a
                  href="https://www.linkedin.com/in/rittermax/"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="h-5 w-5" />
                </a>
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="h-11 w-11 border-primary/50 transition-colors hover:border-primary hover:bg-primary/10"
                asChild
              >
                <a href="mailto:mail@maxritter.net" aria-label="Email">
                  <Mail className="h-5 w-5" />
                </a>
              </Button>
            </nav>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground text-center">
            © {new Date().getFullYear()}{" "}
            <a
              href="https://pilot-shell.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline decoration-primary/50 underline-offset-4 hover:decoration-primary"
            >
              Pilot Shell
            </a>
            . Created by{" "}
            <a
              href="https://maxritter.net/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline decoration-primary/50 underline-offset-4 hover:decoration-primary"
            >
              Max Ritter
            </a>
            . All rights reserved.
            {" · "}
            <a
              href="https://github.com/maxritter/pilot-shell/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline decoration-primary/50 underline-offset-4 hover:decoration-primary"
            >
              License
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
