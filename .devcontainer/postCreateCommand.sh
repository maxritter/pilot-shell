#!/usr/bin/env bash

# Install zsh fzf
echo -e "\nsource <(fzf --zsh)" >>~/.zshrc

# Enable dotenv plugin for automatic .env loading
# This will auto-load .env files when you cd into directories
if ! grep -q "plugins=.*dotenv" ~/.zshrc; then
    # Add dotenv to plugins array if not already present
    sed -i 's/plugins=(/plugins=(dotenv /' ~/.zshrc

    # Disable prompt for auto-loading .env (trust dev container environment)
    echo -e "\n# Auto-load .env files without prompting" >>~/.zshrc
    echo 'export ZSH_DOTENV_PROMPT=false' >>~/.zshrc
fi

# Install uv venv for Python
uv sync --frozen

# Install qlty and initialize
curl https://qlty.sh | sh
echo -e "\nexport QLTY_INSTALL=\"$HOME/.qlty\"" >>~/.zshrc
echo -e 'export PATH=$QLTY_INSTALL/bin:$PATH' >>~/.zshrc
/root/.qlty/bin/qlty check --install-only

# Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Install CC Statusline
curl -fsSL https://raw.githubusercontent.com/hagan/claudia-statusline/main/scripts/quick-install.sh | bash

# Install Dotenvx CLI
curl -sfS https://dotenvx.sh | bash

# Install Cipher
npm install -g @byterover/cipher

# Install Newman
npm install -g newman

# Install Playwright and Firefox Browser
npm install -g @playwright/test && npx playwright install firefox

# Install Python Tools
uv tool install mypy 
uv tool install ruff 
uv tool install basedpyright
uv tool install pytest

# Start Local Postgres with Docker Compose on Port 5433
docker-compose -f .devcontainer/docker-compose.yml up -d

# Add cc alias for quick Claude Code access
echo -e "\n# Claude Code quick alias" >>~/.bashrc
echo 'alias cc="cd /workspaces/claude-code-pro/ && clear && dotenvx run claude"' >>~/.bashrc
echo -e "\n# Claude Code quick alias" >>~/.zshrc
echo 'alias cc="cd /workspaces/claude-code-pro/ && clear && dotenvx run claude"' >>~/.zshrc
