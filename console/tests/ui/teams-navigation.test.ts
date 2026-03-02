import { describe, it, expect } from 'bun:test';
import { SEQUENCE_SHORTCUTS } from '../../src/ui/viewer/constants/shortcuts';

describe('Teams Navigation', () => {
  it('exports TeamsView from views/index.ts', async () => {
    const viewsModule = await import('../../src/ui/viewer/views/index');
    expect(viewsModule.TeamsView).toBeDefined();
    expect(typeof viewsModule.TeamsView).toBe('function');
  });

  it('has teams route in App.tsx routes', async () => {
    const fs = await import('fs/promises');
    const appContent = await fs.readFile(
      'src/ui/viewer/App.tsx',
      'utf-8'
    );

    expect(appContent).toContain('TeamsView');

    expect(appContent).toMatch(/path:\s*['"]\/teams['"]/);
  });

  it('has Teams nav item in sidebar with correct icon', async () => {
    const fs = await import('fs/promises');
    const sidebarContent = await fs.readFile(
      'src/ui/viewer/layouts/Sidebar/SidebarNav.tsx',
      'utf-8'
    );

    expect(sidebarContent).toContain('label: "Teams"');

    expect(sidebarContent).toContain('lucide:users');

    expect(sidebarContent).toMatch(/#\/teams/);
  });

  it('has Go to Teams command in command palette', async () => {
    const fs = await import('fs/promises');
    const paletteContent = await fs.readFile(
      'src/ui/viewer/components/CommandPalette.tsx',
      'utf-8'
    );

    expect(paletteContent).toContain('Go to Teams');

    expect(paletteContent).toContain('G V');

    expect(paletteContent).toMatch(/onNavigate\(['"]\/teams['"]\)/);
  });

  it('has g v keyboard shortcut sequence', () => {
    const teamsShortcut = SEQUENCE_SHORTCUTS.find(
      (s) => s.action === 'navigate:/teams'
    );

    expect(teamsShortcut).toBeDefined();
    expect(teamsShortcut?.sequence).toEqual(['g', 'v']);
    expect(teamsShortcut?.description).toContain('Teams');
  });
});
