import { BlogArticle } from './types';
import content from './worktree-isolation-for-features.md?raw';

export const worktreeIsolationForFeatures: BlogArticle = {
  slug: 'worktree-isolation-for-features',
  title: 'Git Worktree Isolation for AI-Built Features',
  description: 'Run AI work on a separate branch so your main branch stays clean. Squash merge when verified, discard if something goes wrong.',
  date: '2026-01-27',
  author: 'Max Ritter',
  tags: ['Guide', 'Git'],
  readingTime: 4,
  content,
  keywords: 'git worktree, Claude Code isolation, feature branches, squash merge, Claude Code git, safe AI development'
};
