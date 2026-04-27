import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Github, Menu, X, ScrollText, Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { navigateToSection } from "@/utils/navigateToSection";
import { useTheme } from "@/hooks/useTheme";
import boxWebp from "@/assets/box.webp";
import boxPng from "@/assets/box.png";

const navLinks = [
  { label: "Getting Started", href: "#installation" },
  { label: "Demo", href: "#demo" },
  { label: "Usage", href: "#workflow" },
  { label: "What's Inside", href: "#features" },
  { label: "Pricing", href: "#pricing" },
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
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 sm:py-5 flex justify-between items-center">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 sm:gap-3">
          <picture>
            <source srcSet={boxWebp} type="image/webp" />
            <img
              src={boxPng}
              alt="Pilot Shell"
              className="h-8 sm:h-10 w-auto rounded-md border border-primary/20"
              width={128}
              height={128}
            />
          </picture>
        </Link>

        {/* Desktop Navigation */}
        <ul className="hidden lg:flex gap-6 xl:gap-8">
          {navLinks.map((link) => (
            <li key={link.href}>
              <button
                onClick={() => handleSectionClick(link.href)}
                className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors animated-underline"
              >
                {link.label}
              </button>
            </li>
          ))}
        </ul>

        {/* Right side */}
        <div className="flex items-center gap-3 sm:gap-4">
          <Button
            asChild
            variant="outline"
            size="sm"
            className="hidden sm:inline-flex"
          >
            <a href="/docs">Docs</a>
          </Button>
          <a
            href="https://pilot.openchangelog.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Changelog"
          >
            <ScrollText className="h-5 w-5" />
          </a>
          <a
            href="https://github.com/maxritter/pilot-shell"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="GitHub"
          >
            <Github className="h-5 w-5" />
          </a>
          <button
            onClick={toggleTheme}
            className="text-muted-foreground hover:text-foreground transition-colors"
            title={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {resolvedTheme === "dark" ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </button>
          <Button
            onClick={() => handleSectionClick("#installation")}
            className="hidden sm:inline-flex"
            size="sm"
          >
            Get Started
          </Button>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden text-foreground p-2"
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-card border-t border-border px-4 sm:px-6 py-4 animate-fade-in">
          {navLinks.map((link) => (
            <button
              key={link.href}
              onClick={() => handleSectionClick(link.href)}
              className="block w-full text-left py-3 text-muted-foreground hover:text-foreground border-b border-border transition-colors"
            >
              {link.label}
            </button>
          ))}
          <a
            href="/docs"
            className="block w-full text-left py-3 text-muted-foreground hover:text-foreground border-b border-border transition-colors"
          >
            Docs
          </a>
          <Button
            onClick={() => handleSectionClick("#installation")}
            className="mt-4 w-full"
          >
            Get Started
          </Button>
        </div>
      )}
    </nav>
  );
};

export default NavBar;
