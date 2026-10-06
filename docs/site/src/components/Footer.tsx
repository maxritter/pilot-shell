import { Link, useLocation } from "react-router-dom";
import { Logo } from "@/components/NavBar";
import { CONTACT_EMAIL, DOCS_URL, GITHUB_URL, RELEASES_URL } from "@/lib/product";

const Footer = () => {
  const shared = useLocation().pathname.startsWith("/s/");
  return (
  <footer className="w7-ftr">
    <div className="w7-ftr-wrap">
      <div className="w7-ftr-row">
        <Logo small />
        <nav className="w7-ftr-nav" aria-label="Footer">
          <a href={DOCS_URL}>Docs</a>
          <Link to="/pricing">Pricing</Link>
          <a href={GITHUB_URL}>GitHub</a>
          <a href={RELEASES_URL}>Changelog</a>
          <a href={`mailto:${CONTACT_EMAIL}`}>Contact</a>
        </nav>
        <p className="w7-legal">© 2026 QualityLayer · {!shared && "The tasks, people and numbers on this site are an illustration. "}Prices in US dollars, billed monthly through Polar.</p>
      </div>
    </div>
  </footer>
  );
};

export default Footer;
