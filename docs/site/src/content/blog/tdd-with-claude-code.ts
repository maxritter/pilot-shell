import { BlogArticle } from './types';
import content from './tdd-with-claude-code.md?raw';

export const tddWithClaudeCode: BlogArticle = {
  slug: 'tdd-with-claude-code',
  title: 'Enforcing Test-Driven Development with Claude Code',
  description: 'Learn why AI-generated code needs TDD, how to enforce it with hooks and rules, and how Pilot automates the red-green-refactor cycle.',
  date: '2026-02-12',
  author: 'Max Ritter',
  tags: ['Guide', 'Testing'],
  readingTime: 5,
  content,
  keywords: 'Claude Code TDD, AI test-driven development, Claude Code testing, enforce tests Claude, TDD enforcement, red-green-refactor, AI code quality'
};
