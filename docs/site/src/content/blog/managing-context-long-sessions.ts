import { BlogArticle } from './types';
import content from './managing-context-long-sessions.md?raw';

export const managingContextLongSessions: BlogArticle = {
  slug: 'managing-context-long-sessions',
  title: 'Managing Context in Long Claude Code Sessions',
  description: 'Learn how the context window works, what happens when it fills up, and strategies to keep long Claude Code sessions productive without losing progress.',
  date: '2026-02-10',
  author: 'Max Ritter',
  tags: ['Guide', 'Workflow'],
  readingTime: 7,
  content,
  keywords: 'Claude Code context limit, Claude Code session memory, Claude Code long sessions, context window management, autocompaction, Endless Mode'
};
