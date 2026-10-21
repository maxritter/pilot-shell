---
name: website-screenshots
description: Regenerate QualityLayer website and README screenshots from the source App after its UI changes, or when refreshing the developer example gallery.
---

# Website screenshots

Use the website's source App demo and its curated developer projects. The
fixtures in `qualitylayer/src/ui/demo/website-gallery.ts` supply questions,
documents, artifacts and checks; production components supply the interface.
The screenshot command uses a temporary browser profile and in-memory data.

From `docs/site/`, run `npm run screenshots`. It starts and closes its own
loopback source server, renders the twelve scenes in both themes at twice the
pixel density, and writes lossless WebP assets to `public/product/`. The website
and README use these same files. `npm run screenshots -- --only plan,team`
refreshes selected scenes. Dependencies are the locked website and QualityLayer
development dependencies.

Inspect the captured pictures together: the shown project and content must
explain the section, text must be sharp when enlarged, diagrams must have
rendered, and controls must fit. The fixtures show complex example work across
billing, notifications, identity and job processing; keep their scope and
captions consistent when changing them. Capture actual UI rather than drawing
an imitation. The export treatment is monochrome; the App's semantic colors
remain unchanged.

The command rejects internal beta-build content, remote requests and real API
calls. A failing scene leaves its last good published image in place; fix the
fixture or selector and rerun it. Review `capture-manifest.json` alongside the
images. Run the focused site checks and a desktop/phone pass of the affected
gallery and its full-size image dialog.

This skill updates local assets. Commit, deploy and replace Claude Design
pages only within the user's current authorization. Use the existing
deploy-website and open-claude-design skills for those destinations.
