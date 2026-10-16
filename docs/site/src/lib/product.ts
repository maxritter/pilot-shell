/** Facts the whole site shares. Change them here, nowhere else. */
export const SITE_URL = "https://qualitylayer.dev";
/** Mirrors the CLI's offline window; copy.test.tsx checks the rendered claim against its constant. */
export const OFFLINE_DAYS = 7;

/** Served from the site (a redirect to the installer in the repository). */
export const INSTALL_COMMAND = `curl -fsSL ${SITE_URL}/install.sh | bash`;

export const GITHUB_URL = "https://github.com/maxritter/pilot-shell";
/** The documentation, served by Docusaurus under the site's own domain. */
export const DOCS_URL = "/docs/";
export const RELEASES_URL = `${GITHUB_URL}/releases`;
export const CHANGELOG_URL = "/docs/changelog";
export const CONTACT_EMAIL = "mail@maxritter.net";
export const AUTHOR_URL = "https://maxritter.net";
export const AUTHOR_NAME = "Max Ritter";

/** The hero's subtitle and the default page description. */
export const DESCRIPTION =
  "Plan each change visually with your agent and your team: the architecture as diagrams, the screens as clickable designs, every decision in the open. When everyone shares the same picture, your agents build it.";
/** The line under the name wherever the product is introduced: the hero, page titles, the README and the CLI. */
export const SLOGAN = "The software factory with you in the loop";
/** The sentence shown when the site is shared or listed in search; also rendered at build time. */
export const SHARE_DESCRIPTION =
  "Visual planning and spec-driven development with Claude Code and Codex. Review the plan, keep a human in the loop, and let your agents build it.";
/** One engineer's words about QualityLayer, relayed by Max on 2026-10-15. Quote it as it is; the attribution stays anonymous. */
export const ENGINEER_QUOTE = "With QualityLayer, developing software with agents finally feels like doing real engineering again.";
