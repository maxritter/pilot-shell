import { Link, useLocation, useNavigate } from "react-router-dom";
import { Github, Linkedin, Mail } from "lucide-react";
import { navigateToSection } from "@/utils/navigateToSection";
import { PORTAL_URL } from "@/lib/links";

const Footer = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const goToSection = (id: string) => navigateToSection(id, location.pathname, navigate);

  return (
    <footer className="ps-foot" role="contentinfo">
      <div className="ps-ctr ps-stg">
        <Link to="/" className="ps-brand" aria-label="Pilot Shell home">
          <img className="ps-mark" src="/box.webp" alt="" width={28} height={28} decoding="async" />
          <span className="ps-brand-t">Pilot Shell</span>
        </Link>
        <p className="ps-ftag">How real engineers run Claude Code and Codex</p>

        <nav className="ps-flinks" aria-label="Footer">
          <button type="button" className="ps-fl" onClick={() => goToSection("installation")}>
            Getting Started
          </button>
          <button type="button" className="ps-fl" onClick={() => goToSection("anatomy")}>
            The Harness
          </button>
          <a className="ps-fl" href="/docs">
            Docs
          </a>
          <Link className="ps-fl" to="/pricing">
            Subscribe
          </Link>
          <a className="ps-fl" href={PORTAL_URL} target="_blank" rel="noopener noreferrer">
            Manage Subscription
          </a>
          <button type="button" className="ps-fl" onClick={() => goToSection("faq")}>
            FAQ
          </button>
          <a
            className="ps-fl"
            href="https://github.com/maxritter/pilot-shell/releases"
            target="_blank"
            rel="noopener noreferrer"
          >
            Changelog
          </a>
        </nav>

        <nav className="ps-socials" aria-label="Social media links">
          <a
            className="ps-soc"
            href="https://github.com/maxritter/pilot-shell"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub"
          >
            <Github className="h-5 w-5" aria-hidden="true" />
          </a>
          <a
            className="ps-soc"
            href="https://www.linkedin.com/in/rittermax/"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
          >
            <Linkedin className="h-5 w-5" aria-hidden="true" />
          </a>
          <a className="ps-soc" href="mailto:mail@maxritter.net" aria-label="Email">
            <Mail className="h-5 w-5" aria-hidden="true" />
          </a>
        </nav>

        <p className="ps-copy">
          © {new Date().getFullYear()}{" "}
          <a href="https://pilot-shell.com/" target="_blank" rel="noopener noreferrer">
            Pilot Shell
          </a>
          . Created by{" "}
          <a href="https://maxritter.net/" target="_blank" rel="noopener noreferrer">
            Max Ritter
          </a>
          . All rights reserved.
          {" · "}
          <a
            href="https://github.com/maxritter/pilot-shell/blob/main/LICENSE"
            target="_blank"
            rel="noopener noreferrer"
          >
            License
          </a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;
