#!/usr/bin/env bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
  echo "Usage: $0 <version>"
  echo ""
  echo "Example: $0 v2.1.3"
  echo ""
  echo "This script will:"
  echo "  1. Update the installation URL in README.md with the new version"
  echo "  2. Commit the change"
  echo "  3. Create a git tag with the version"
  exit 1
}

# Check if version argument is provided
if [ $# -eq 0 ]; then
  echo -e "${RED}Error: Version argument is required${NC}"
  usage
fi

VERSION="$1"

# Validate version format (should start with 'v' followed by semantic version)
if ! [[ $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-.*)?$ ]]; then
  echo -e "${YELLOW}Warning: Version format '$VERSION' doesn't match semantic versioning (e.g., v2.1.3)${NC}"
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo -e "${RED}Error: Not in a git repository${NC}"
  exit 1
fi

# Check if README.md exists
if [ ! -f "README.md" ]; then
  echo -e "${RED}Error: README.md not found in current directory${NC}"
  exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
  git status --short
  read -p "Continue with release? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Check if tag already exists
if git rev-parse "$VERSION" >/dev/null 2>&1; then
  echo -e "${RED}Error: Git tag '$VERSION' already exists${NC}"
  exit 1
fi

echo -e "${GREEN}Starting release process for version $VERSION${NC}"
echo ""

# Update README.md installation URL
# The line should contain: curl -sSL https://raw.githubusercontent.com/maxritter/claude-codepro/vX.X.X/scripts/install.sh | bash
echo "📝 Updating README.md installation URL with version $VERSION..."

# First, check if the URL pattern exists
if ! grep -q "raw.githubusercontent.com/maxritter/claude-codepro/v" README.md; then
  echo -e "${RED}Error: Installation URL pattern not found in README.md${NC}"
  echo "Expected pattern: https://raw.githubusercontent.com/maxritter/claude-codepro/v*.*.*"
  exit 1
fi

# Get the current version from README.md
CURRENT_VERSION=$(grep -o "claude-codepro/v[0-9]\+\.[0-9]\+\.[0-9]\+[^/]*" README.md | head -1 | sed 's/.*\(v[0-9]\+\.[0-9]\+\.[0-9]\+[^/]*\).*/\1/')

if [ -z "$CURRENT_VERSION" ]; then
  echo -e "${RED}Error: Could not detect current version in README.md${NC}"
  exit 1
fi

echo "  Current version: $CURRENT_VERSION"
echo "  New version: $VERSION"

# Use sed to replace the version in the URL
# macOS (BSD) sed requires a backup extension or '', Linux (GNU) sed differs
if sed --version 2>&1 | grep -q GNU; then
  # GNU sed (Linux)
  sed -i -E "s|claude-codepro/v[0-9]+\.[0-9]+\.[0-9]+/scripts/install\.sh|claude-codepro/$VERSION/scripts/install.sh|g" README.md
else
  # BSD sed (macOS)
  sed -i '' -E "s|claude-codepro/v[0-9]+\.[0-9]+\.[0-9]+/scripts/install\.sh|claude-codepro/$VERSION/scripts/install.sh|g" README.md
fi

# Verify the change
if grep -q "claude-codepro/$VERSION/scripts/install.sh" README.md; then
  echo -e "${GREEN}✓ README.md updated successfully${NC}"
  UPDATED_LINE=$(grep "claude-codepro/$VERSION/scripts/install.sh" README.md | xargs)
  echo "  URL now contains: ...${UPDATED_LINE:60:80}..."
else
  echo -e "${RED}Error: Failed to update README.md${NC}"
  exit 1
fi

# Commit the change
echo ""
echo "📦 Committing changes..."
git add README.md
git commit -m "chore: bump version to $VERSION" || {
  echo -e "${RED}Error: Failed to commit changes${NC}"
  exit 1
}
echo -e "${GREEN}✓ Changes committed${NC}"

# Create git tag
echo ""
echo "🏷️  Creating git tag $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION" || {
  echo -e "${RED}Error: Failed to create git tag${NC}"
  exit 1
}
echo -e "${GREEN}✓ Git tag created${NC}"

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Release $VERSION completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git show $VERSION"
echo "  2. Push the commit: git push origin main"
echo "  3. Push the tag: git push origin $VERSION"
echo ""
echo "Or push both at once:"
echo "  git push origin main --tags"
