import { BlogArticle } from './types';
import content from './slash-commands-and-init.md?raw';

export const slashCommandsAndInit: BlogArticle = {
  slug: 'slash-commands-and-init',
  title: 'Custom Slash Commands and --init for Claude Code',
  description: 'Create reusable slash commands and use --init to load different context per session type. Package complex instructions into single invocations.',
  date: '2026-01-30',
  author: 'Max Ritter',
  tags: ['Guide', 'Configuration'],
  readingTime: 4,
  content,
  keywords: 'Claude Code commands, slash commands, Claude Code init, custom commands, Claude Code workflow, session context'
};
