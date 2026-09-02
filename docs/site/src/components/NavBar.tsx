import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { BookOpen, Github, Menu, Moon, Newspaper, Sun, X } from "lucide-react";
import { navigateToSection } from "@/utils/navigateToSection";
import { useScrollSpy } from "@/hooks/use-reveal";
import { useTheme } from "@/hooks/useTheme";

const sectionLinks = [
  { id: "anatomy", label: "The Harness" },
  { id: "workflows", label: "Workflows" },
  { id: "shift-left", label: "Teams" },
  { id: "console", label: "Console" },
  { id: "faq", label: "FAQ" },
];

const externalLinks = [
  { label: "Docs", href: "/docs", icon: BookOpen },
  { label: "Blog", href: "/blog", icon: Newspaper },
];

const NavBar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolledPastHeader, setScrolledPastHeader] = useState(false);
  const headerRef = useRef<HTMLElement>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { resolvedTheme, setThemePreference } = useTheme();

  // The section row only means something on the homepage, where the sections live.
  const showSectionNav = location.pathname === "/";
  const activeSection = useScrollSpy(showSectionNav);

  const themeLabel =
    resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode";

  const toggleTheme = () => {
    setThemePreference(resolvedTheme === "dark" ? "light" : "dark");
  };

  const handleSectionClick = (id: string) => {
    navigateToSection(id, location.pathname, navigate);
    setMobileMenuOpen(false);
  };

  // The compact brand + CTA slide into the sticky row once the main bar is gone.
  useEffect(() => {
    const header = headerRef.current;
    if (!header) return;
    const observer = new IntersectionObserver(
      ([entry]) => setScrolledPastHeader(!entry.isIntersecting),
      { threshold: 0 },
    );
    observer.observe(header);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileMenuOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [mobileMenuOpen]);

  return (
    <>
      <header className="ps-bar-a" ref={headerRef}>
        <div className="ps-ctr ps-row-a">
          <Link to="/" className="ps-brand" aria-label="Pilot Shell home">
            <img className="ps-mark" src="/box.webp" alt="" width={28} height={28} decoding="async" />
            <span className="ps-brand-t">Pilot Shell</span>
          </Link>

          <nav className="ps-util" aria-label="Site">
            <div className="ps-util-links">
              {externalLinks.map((link) => (
                <a key={link.href} className="ps-nl" href={link.href}>
                  {link.label}
                </a>
              ))}
            </div>
            <div className="ps-ico-grp">
              <a
                className="ps-ibtn ps-gh"
                href="https://github.com/maxritter/pilot-shell"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub repository"
              >
                <Github className="h-[18px] w-[18px]" aria-hidden="true" />
              </a>
              <button type="button" className="ps-ibtn" onClick={toggleTheme} aria-label={themeLabel} title={themeLabel}>
                {resolvedTheme === "dark" ? (
                  <Sun className="h-[18px] w-[18px]" aria-hidden="true" />
                ) : (
                  <Moon className="h-[18px] w-[18px]" aria-hidden="true" />
                )}
              </button>
              <button
                type="button"
                className="ps-ibtn ps-ham"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                aria-expanded={mobileMenuOpen}
                aria-controls="mobile-menu"
              >
                {mobileMenuOpen ? (
                  <X className="h-[18px] w-[18px]" aria-hidden="true" />
                ) : (
                  <Menu className="h-[18px] w-[18px]" aria-hidden="true" />
                )}
              </button>
            </div>
            <Link className="ps-btn ps-btn-sm ps-btn-sec" to="/pricing">
              Subscribe
            </Link>
          </nav>
        </div>

        {mobileMenuOpen && (
          <div className="ps-mpanel" id="mobile-menu">
            {showSectionNav &&
              sectionLinks.map((link) => (
                <button key={link.id} type="button" onClick={() => handleSectionClick(link.id)}>
                  {link.label}
                </button>
              ))}
            {externalLinks.map((link) => (
              <a key={link.href} href={link.href} onClick={() => setMobileMenuOpen(false)}>
                <link.icon className="h-4 w-4" aria-hidden="true" />
                {link.label}
              </a>
            ))}
            <a href="https://github.com/maxritter/pilot-shell" target="_blank" rel="noopener noreferrer">
              <Github className="h-4 w-4" aria-hidden="true" />
              GitHub
            </a>
            <Link className="ps-btn ps-btn-sm ps-btn-sec" to="/pricing" onClick={() => setMobileMenuOpen(false)}>
              Subscribe
            </Link>
          </div>
        )}
      </header>

      {showSectionNav && (
        <div className={`ps-bar-b${scrolledPastHeader ? " ps-stuck" : ""}`}>
          <div className="ps-ctr ps-row-b">
            <Link to="/" className="ps-brand ps-brand-c" aria-label="Pilot Shell home" tabIndex={scrolledPastHeader ? 0 : -1}>
              <img className="ps-mark" src="/box.webp" alt="" width={28} height={28} decoding="async" />
              <span className="ps-brand-t">Pilot Shell</span>
            </Link>
            <nav className="ps-secnav" aria-label="Page sections">
              {sectionLinks.map((link) => (
                <a
                  key={link.id}
                  className="ps-sl"
                  href={`#${link.id}`}
                  aria-current={activeSection === link.id ? "location" : undefined}
                  onClick={(event) => {
                    event.preventDefault();
                    handleSectionClick(link.id);
                  }}
                >
                  <span className="ps-dot" aria-hidden="true" />
                  {link.label}
                </a>
              ))}
            </nav>
            <Link
              className="ps-btn ps-btn-sm ps-btn-sec ps-cta-c"
              to="/pricing"
              tabIndex={scrolledPastHeader ? 0 : -1}
            >
              Subscribe
            </Link>
          </div>
        </div>
      )}
    </>
  );
};

export default NavBar;
