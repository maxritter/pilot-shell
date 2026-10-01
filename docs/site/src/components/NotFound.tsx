import { Link } from "react-router-dom";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import { SITE_URL } from "@/lib/product";

const NotFoundComponent = () => (
  <>
    <SEO title="Page not found — QualityLayer" description="The page you are looking for does not exist." canonicalUrl={`${SITE_URL}/404`} />
    <Page>
      <section className="w7-sec w7-nf" aria-labelledby="nf-h">
        <div className="w7-wrap">
          <h1 id="nf-h" className="w7-h2">Page not found</h1>
          <p className="w7-lead">That page does not exist, or it has moved.</p>
          <div className="w7-btns w7-figure"><Link className="w7-btn-p" to="/">Back to the home page</Link><a className="w7-btn-s" href="/docs/">Open the docs</a></div>
        </div>
      </section>
    </Page>
  </>
);

export default NotFoundComponent;
