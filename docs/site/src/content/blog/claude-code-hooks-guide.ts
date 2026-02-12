import { BlogArticle } from './types';
import content from './claude-code-hooks-guide.md?raw';

export const claudeCodeHooksGuide: BlogArticle = {
  slug: 'claude-code-hooks-guide',
  title: 'A Practical Guide to Claude Code Hooks',
  description: 'Learn how to use Claude Code hooks to auto-lint, block dangerous commands, load context, and verify work. Includes configuration examples.',
  date: '2026-02-12',
  author: 'Max Ritter',
  tags: ['Guide', 'Hooks'],
  readingTime: 5,
  content,
  keywords: 'Claude Code hooks, PreToolUse, PostToolUse, Stop hook, SessionStart, Claude Code automation, Claude Code settings'
};
