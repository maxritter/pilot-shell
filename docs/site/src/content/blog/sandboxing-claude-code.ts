import { BlogArticle } from './types';
import content from './sandboxing-claude-code.md?raw';

export const sandboxingClaudeCode: BlogArticle = {
  slug: 'sandboxing-claude-code',
  title: 'Sandboxing Claude Code for Safe Execution',
  description: 'Add OS-level filesystem and network isolation to Claude Code. Covers macOS Seatbelt, Linux bubblewrap, and Docker.',
  date: '2026-01-22',
  author: 'Max Ritter',
  tags: ['Guide', 'Security'],
  readingTime: 4,
  content,
  keywords: 'Claude Code sandbox, Claude Code security, macOS Seatbelt, bubblewrap, Docker Claude Code, AI sandboxing'
};
