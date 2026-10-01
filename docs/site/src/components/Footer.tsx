import { Link } from "react-router-dom";
import { Logo } from "@/components/NavBar";
import { CONTACT_EMAIL, DOCS_URL, GITHUB_URL, RELEASES_URL } from "@/lib/product";

const Footer = () => (
  <footer className="w7-ftr">
    <div className="w7-ftr-wrap">
      <p className="w7-ftr-tag">The missing <span className="w7-accent">quality layer</span> for your coding agents.</p>
      <div className="w7-ftr-row">
        <Logo small />
        <nav className="w7-ftr-nav" aria-label="Footer">
          <a href={DOCS_URL}>Docs</a>
          <Link to="/pricing">Pricing</Link>
          <a href={GITHUB_URL}>GitHub</a>
          <a href={RELEASES_URL}>Changelog</a>
          <a href={`mailto:${CONTACT_EMAIL}`}>Contact</a>
        </nav>
        <p className="w7-legal">© 2026 QualityLayer · Tasks, code and evidence on this site are illustrative. Prices in US dollars, billed monthly through Polar.</p>
      </div>
    </div>
  </footer>
);

export default Footer;
