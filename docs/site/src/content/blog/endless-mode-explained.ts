import { BlogArticle } from './types';
import content from './endless-mode-explained.md?raw';

export const endlessModeExplained: BlogArticle = {
  slug: 'endless-mode-explained',
  title: 'How Endless Mode Keeps Claude Working Without Limits',
  description: 'Claude Code has a context limit. Endless Mode automatically saves state and restarts sessions so your work never stops.',
  date: '2026-02-09',
  author: 'Max Ritter',
  tags: ['Feature', 'Workflow'],
  readingTime: 4,
  content,
  keywords: 'Claude Code context limit, Endless Mode, Claude Code session, context window, Claude Code unlimited, session continuation'
};
