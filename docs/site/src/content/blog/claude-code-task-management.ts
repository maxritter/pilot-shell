import { BlogArticle } from './types';
import content from './claude-code-task-management.md?raw';

export const claudeCodeTaskManagement: BlogArticle = {
  slug: 'claude-code-task-management',
  title: 'Multi-Session Task Management in Claude Code',
  description: 'Track work across sessions with built-in task management. Dependencies, progress tracking, and cross-session persistence.',
  date: '2026-02-06',
  author: 'Max Ritter',
  tags: ['Guide', 'Workflow'],
  readingTime: 4,
  content,
  keywords: 'Claude Code tasks, task management, multi-session, Claude Code workflow, task dependencies, progress tracking'
};
