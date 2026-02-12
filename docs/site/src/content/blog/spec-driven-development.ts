import { BlogArticle } from './types';
import content from './spec-driven-development.md?raw';

export const specDrivenDevelopment: BlogArticle = {
  slug: 'spec-driven-development',
  title: 'Spec-Driven Development with Claude Code',
  description: 'Structure large features with a plan-implement-verify loop. Stop Claude from drifting and ensure every feature matches your requirements.',
  date: '2026-02-10',
  author: 'Max Ritter',
  tags: ['Guide', 'Workflow'],
  readingTime: 5,
  content,
  keywords: 'Claude Code spec, spec-driven development, Claude Code planning, AI development workflow, Claude Code features, structured AI coding'
};
