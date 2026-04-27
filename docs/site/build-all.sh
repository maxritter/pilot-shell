#!/bin/bash
# Build both the Vite landing page and Docusaurus docs, combine into single output.
# Output: docs/site/dist/ (Vite) with docs/site/dist/docs/ (Docusaurus)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="$SCRIPT_DIR"
DOCUSAURUS_DIR="$SCRIPT_DIR/../docusaurus"

echo "=== Building Vite landing page ==="
cd "$SITE_DIR"
npm ci --prefer-offline 2>/dev/null || npm install
npm run build

echo "=== Building Docusaurus docs ==="
cd "$DOCUSAURUS_DIR"
npm ci --prefer-offline 2>/dev/null || npm install
npm run build

echo "=== Combining outputs ==="
DIST="$SITE_DIR/dist"
BUILD="$DOCUSAURUS_DIR/build"

# Copy Docusaurus docs into Vite dist
cp -r "$BUILD/docs" "$DIST/docs"

# Merge Docusaurus assets into Vite assets (no filename conflicts — Vite uses hashes, Docusaurus uses css/js subdirs)
cp -r "$BUILD/assets/"* "$DIST/assets/"

# Copy search plugin files
[ -d "$BUILD/search" ] && cp -r "$BUILD/search" "$DIST/search"
[ -f "$BUILD/search-index.json" ] && cp "$BUILD/search-index.json" "$DIST/search-index.json"

# Copy Docusaurus img (favicon etc.) — merge into existing img or create
[ -d "$BUILD/img" ] && cp -r "$BUILD/img" "$DIST/img"

# Move Docusaurus's sitemap into /docs/ so it doesn't overwrite the Vite-generated
# sitemap index at /sitemap.xml (which references both pages and docs sitemaps).
if [ -f "$BUILD/sitemap.xml" ]; then
  cp "$BUILD/sitemap.xml" "$DIST/docs/sitemap.xml"
fi
# Copy any other Docusaurus xml files (rss, atom, etc.) to /docs/
for f in "$BUILD"/*.xml; do
  if [ -f "$f" ] && [ "$(basename "$f")" != "sitemap.xml" ]; then
    cp "$f" "$DIST/docs/" 2>/dev/null || true
  fi
done

echo "=== Build complete ==="
echo "Landing page: $DIST/"
echo "Documentation: $DIST/docs/"
echo ""
echo "File counts:"
echo "  docs: $(find "$DIST/docs" -name '*.html' | wc -l | tr -d ' ') pages"
