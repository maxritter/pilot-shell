/**
 * Tests for ViewerRoutes hash redirect and static middleware fix
 *
 * Verifies two bug fixes:
 * 1. express.static has `index: false` so GET / is handled by handleViewerUI
 *    (not intercepted by static middleware serving index.html without version injection)
 * 2. handleViewerUI prefers index.html (Vite build output) over viewer.html
 * 3. index.html template contains hash redirect script so http://localhost:41777
 *    works the same as http://localhost:41777/#/
 *
 * Mock Justification: Source code inspection (no mocks needed).
 * These are structural/configuration properties verified statically.
 */
import { describe, it, expect } from 'bun:test';
import { readFileSync } from 'fs';
import path from 'path';

const VIEWER_ROUTES_PATH = path.join(
  import.meta.dir,
  '../../src/services/worker/http/routes/ViewerRoutes.ts',
);

const INDEX_HTML_PATH = path.join(
  import.meta.dir,
  '../../src/ui/viewer/index.html',
);

describe('ViewerRoutes: hash redirect bug fix', () => {
  describe('express.static configuration', () => {
    it('should have index: false on express.static to prevent intercepting GET /', () => {
      const source = readFileSync(VIEWER_ROUTES_PATH, 'utf-8');

      // express.static should be called with index: false so it does NOT serve
      // index.html for GET / — that must go to handleViewerUI
      expect(source).toContain('index: false');
    });

    it('should not use default index.html serving (would bypass handleViewerUI)', () => {
      const source = readFileSync(VIEWER_ROUTES_PATH, 'utf-8');

      // Verify express.static call includes index: false explicitly
      const staticCallMatch = source.match(/express\.static\(uiPath[\s\S]*?\)/);
      expect(staticCallMatch).toBeTruthy();
      expect(staticCallMatch![0]).toContain('index: false');
    });
  });

  describe('handleViewerUI: HTML file preference', () => {
    it('should look for index.html before viewer.html', () => {
      const source = readFileSync(VIEWER_ROUTES_PATH, 'utf-8');

      const indexHtmlPos = source.indexOf('"index.html"');
      const viewerHtmlPos = source.indexOf('"viewer.html"');

      expect(indexHtmlPos).toBeGreaterThan(-1);
      expect(viewerHtmlPos).toBeGreaterThan(-1);
      // index.html must appear first (higher priority)
      expect(indexHtmlPos).toBeLessThan(viewerHtmlPos);
    });

    it('should prefer ui/index.html (Vite build output) as primary path', () => {
      const source = readFileSync(VIEWER_ROUTES_PATH, 'utf-8');

      // The viewerPaths array should list index.html first
      const viewerPathsMatch = source.match(/viewerPaths\s*=\s*\[[\s\S]*?\]/);
      expect(viewerPathsMatch).toBeTruthy();

      const viewerPathsBlock = viewerPathsMatch![0];
      const indexHtmlPos = viewerPathsBlock.indexOf('index.html');
      const viewerHtmlPos = viewerPathsBlock.indexOf('viewer.html');

      expect(indexHtmlPos).toBeGreaterThan(-1);
      expect(indexHtmlPos).toBeLessThan(viewerHtmlPos);
    });
  });

  describe('index.html: hash router initialization', () => {
    it('should contain hash redirect script for environments without hash fragment', () => {
      const html = readFileSync(INDEX_HTML_PATH, 'utf-8');

      // Must redirect to #/ when hash is empty so http://localhost:41777 works
      // same as http://localhost:41777/#/
      expect(html).toContain("location.replace('#/')");
    });

    it('should have hash redirect script before the module script', () => {
      const html = readFileSync(INDEX_HTML_PATH, 'utf-8');

      const hashRedirectPos = html.indexOf("location.replace('#/')");
      const moduleScriptPos = html.indexOf('type="module"');

      expect(hashRedirectPos).toBeGreaterThan(-1);
      expect(moduleScriptPos).toBeGreaterThan(-1);
      // Hash redirect must run before the React app loads
      expect(hashRedirectPos).toBeLessThan(moduleScriptPos);
    });

    it('should only redirect when hash is empty (not for existing hash routes)', () => {
      const html = readFileSync(INDEX_HTML_PATH, 'utf-8');

      // Must guard the redirect with a check so existing hash routes are unaffected
      expect(html).toContain('location.hash');
    });
  });
});
