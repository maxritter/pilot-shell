/** Facts the whole site shares. Change them here, nowhere else. */
export const SITE_URL = "https://qualitylayer.dev";

/** Served from the site (a redirect to the installer in the repository). */
export const INSTALL_COMMAND = `curl -fsSL ${SITE_URL}/install.sh | bash`;

export const GITHUB_URL = "https://github.com/maxritter/pilot-shell";
/** The documentation, served by Docusaurus under the site's own domain. */
export const DOCS_URL = "/docs/";
export const RELEASES_URL = `${GITHUB_URL}/releases`;
export const CONTACT_EMAIL = "mail@maxritter.net";
export const AUTHOR_URL = "https://maxritter.net";
export const AUTHOR_NAME = "Max Ritter";

export const DESCRIPTION =
  "You approve the plan before any code is written. Your agent builds it in small, tested steps, and an independent check compares it with what you asked.";
