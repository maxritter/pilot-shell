import { BlogArticle } from './types';
import content from './self-validating-ai-agents.md?raw';

export const selfValidatingAiAgents: BlogArticle = {
  slug: 'self-validating-ai-agents',
  title: 'Building Self-Validating AI Agents with Claude Code',
  description: 'Use Stop hooks, PostToolUse validation, and review agents to ensure Claude checks its own work before responding.',
  date: '2026-02-03',
  author: 'Max Ritter',
  tags: ['Guide', 'Agents'],
  readingTime: 4,
  content,
  keywords: 'Claude Code agents, self-validating AI, Stop hook, AI code review, Claude Code validation, AI quality assurance'
};
