import { BlogArticle } from './types';
import content from './claude-code-rules-guide.md?raw';

export const claudeCodeRulesGuide: BlogArticle = {
  slug: 'claude-code-rules-guide',
  title: 'The Complete Guide to Claude Code Rules',
  description: 'Everything you need to know about Claude Code rules: types, locations, frontmatter, writing effective rules, practical examples, and team management.',
  date: '2026-02-08',
  author: 'Max Ritter',
  tags: ['Guide', 'Configuration'],
  readingTime: 5,
  content,
  keywords: 'Claude Code rules, CLAUDE.md, Claude Code custom instructions, Claude Code configuration, Claude Code rules guide'
};
