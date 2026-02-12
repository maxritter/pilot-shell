import { BlogArticle } from './types';
import content from './claude-code-settings-reference.md?raw';

export const claudeCodeSettingsReference: BlogArticle = {
  slug: 'claude-code-settings-reference',
  title: 'Claude Code Settings: What You Can Configure',
  description: 'A concise reference for Claude Code settings: scopes, permissions, hooks, MCP servers, environment variables, and project vs user configuration.',
  date: '2026-02-07',
  author: 'Max Ritter',
  tags: ['Reference', 'Configuration'],
  readingTime: 5,
  content,
  keywords: 'Claude Code settings, settings.json, Claude Code configuration, Claude Code permissions, Claude Code environment variables'
};
