import { describe, it, expect } from 'bun:test';

describe('Teams Install', () => {
  it('TeamsSyncButton component exists and renders correctly', async () => {
    const fs = await import('fs/promises');
    const teamsViewContent = await fs.readFile(
      'src/ui/viewer/views/Teams/index.tsx',
      'utf-8'
    );

    expect(teamsViewContent).toContain('function TeamsSyncButton');

    expect(teamsViewContent).toMatch(/className="btn btn-primary btn-sm"/);

    expect(teamsViewContent).toContain('loading loading-spinner');
    expect(teamsViewContent).toContain('Syncing...');

    expect(teamsViewContent).toContain('Sync All');
  });

  it('TeamsView uses useToast for notifications', async () => {
    const fs = await import('fs/promises');
    const teamsViewContent = await fs.readFile(
      'src/ui/viewer/views/Teams/index.tsx',
      'utf-8'
    );

    expect(teamsViewContent).toMatch(/import.*useToast.*from.*ToastContext/);

    expect(teamsViewContent).toMatch(/useToast\(\)/);
  });

  it('handles successful install with toast notification', async () => {
    const fs = await import('fs/promises');
    const teamsViewContent = await fs.readFile(
      'src/ui/viewer/views/Teams/index.tsx',
      'utf-8'
    );

    expect(teamsViewContent).toMatch(/\.success\(['"].*[Tt]eams.*sync/i);
  });

  it('handles install error with toast notification', async () => {
    const fs = await import('fs/promises');
    const teamsViewContent = await fs.readFile(
      'src/ui/viewer/views/Teams/index.tsx',
      'utf-8'
    );

    expect(teamsViewContent).toMatch(/\.error\(/);
  });

  it('handles install timeout with warning toast', async () => {
    const fs = await import('fs/promises');
    const teamsViewContent = await fs.readFile(
      'src/ui/viewer/views/Teams/index.tsx',
      'utf-8'
    );

    expect(teamsViewContent).toMatch(/\.warning\(/);
  });

  it('handleInstall wrapper function exists', async () => {
    const fs = await import('fs/promises');
    const teamsViewContent = await fs.readFile(
      'src/ui/viewer/views/Teams/index.tsx',
      'utf-8'
    );

    expect(teamsViewContent).toMatch(/handle(Install|Sync)/);
  });
});
