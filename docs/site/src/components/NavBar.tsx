import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu, X, Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { navigateToSection } from "@/utils/navigateToSection";
import { useTheme } from "@/hooks/useTheme";

const sectionLinks = [
  { label: "The Harness", href: "#anatomy" },
  { label: "Workflows", href: "#workflows" },
  { label: "Teams", href: "#shift-left" },
  { label: "Console", href: "#console" },
  { label: "FAQ", href: "#faq" },
];

const externalLinks = [
  { label: "Docs", href: "/docs" },
  { label: "Blog", href: "/blog" },
];

const NavBar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { resolvedTheme, setThemePreference } = useTheme();

  const toggleTheme = () => {
    setThemePreference(resolvedTheme === "dark" ? "light" : "dark");
  };

  const handleSectionClick = (href: string) => {
    navigateToSection(href, location.pathname, navigate);
    setMobileMenuOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border/50">
      <div className="flex justify-between items-center px-4 sm:px-6 lg:px-10 py-3">
        {/* Logo */}
        <Link
          to="/"
          aria-label="Pilot Shell home"
          className="flex items-center gap-2.5"
        >
          <img
            src="/box.webp"
            alt=""
            className="h-[26px] w-[26px] rounded-[6px]"
            width={26}
            height={26}
            decoding="async"
          />
          <span className="text-[14.5px] font-semibold tracking-[-0.01em] text-foreground">
            Pilot Shell
          </span>
        </Link>

        {/* Desktop: links + actions as one right-aligned group, per the design */}
        <div className="flex items-center gap-1.5">
          <div className="hidden lg:flex items-center gap-1.5">
            {sectionLinks.map((link) => (
              <button
                key={link.href}
                onClick={() => handleSectionClick(link.href)}
                className="animated-underline text-muted-foreground hover:text-foreground text-[13px] font-medium transition-colors px-2.5 py-2"
              >
                {link.label}
              </button>
            ))}
            {externalLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="animated-underline text-muted-foreground hover:text-foreground text-[13px] font-medium transition-colors px-2.5 py-2"
              >
                {link.label}
              </a>
            ))}
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            className="text-muted-foreground hover:text-foreground transition-colors p-2"
            title={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            aria-label={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {resolvedTheme === "dark" ? (
              <Sun className="h-[18px] w-[18px]" aria-hidden="true" />
            ) : (
              <Moon className="h-[18px] w-[18px]" aria-hidden="true" />
            )}
          </button>
          <Button asChild size="sm" className="hidden sm:inline-flex ml-2.5">
            <Link to="/pricing">Subscribe</Link>
          </Button>
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden text-foreground p-2"
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" aria-hidden="true" />
            ) : (
              <Menu className="h-5 w-5" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-card border-t border-border px-4 sm:px-6 py-4 animate-fade-in">
          {sectionLinks.map((link) => (
            <button
              key={link.href}
              onClick={() => handleSectionClick(link.href)}
              className="block w-full text-left py-3 text-muted-foreground hover:text-foreground border-b border-border transition-colors"
            >
              {link.label}
            </button>
          ))}
          {externalLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="block w-full text-left py-3 text-muted-foreground hover:text-foreground border-b border-border transition-colors"
            >
              {link.label}
            </a>
          ))}
          <Button asChild className="mt-4 w-full">
            <Link to="/pricing" onClick={() => setMobileMenuOpen(false)}>
              Subscribe
            </Link>
          </Button>
        </div>
      )}
    </nav>
  );
};

export default NavBar;
