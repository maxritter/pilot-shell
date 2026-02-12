import { BlogArticle } from './types';
import { tddWithClaudeCode } from './tdd-with-claude-code';
import { managingContextLongSessions } from './managing-context-long-sessions';
import { claudeCodeRulesGuide } from './claude-code-rules-guide';
import { claudeCodeHooksGuide } from './claude-code-hooks-guide';
import { mcpServersClaudeCode } from './mcp-servers-claude-code';
import { specDrivenDevelopment } from './spec-driven-development';
import { endlessModeExplained } from './endless-mode-explained';
import { persistentMemoryAcrossSessions } from './persistent-memory-across-sessions';
import { claudeCodeSettingsReference } from './claude-code-settings-reference';
import { claudeCodeTaskManagement } from './claude-code-task-management';
import { terminalSetupForClaudeCode } from './terminal-setup-for-claude-code';
import { selfValidatingAiAgents } from './self-validating-ai-agents';
import { slashCommandsAndInit } from './slash-commands-and-init';
import { worktreeIsolationForFeatures } from './worktree-isolation-for-features';
import { onlineLearningTeachingClaude } from './online-learning-teaching-claude';
import { sandboxingClaudeCode } from './sandboxing-claude-code';
import { teamVaultSharingAiAssets } from './team-vault-sharing-ai-assets';
import { choosingTheRightClaudeModel } from './choosing-the-right-claude-model';
import { context7LibraryDocs } from './context7-library-docs';

export const articles: BlogArticle[] = [
  tddWithClaudeCode,
  managingContextLongSessions,
  claudeCodeRulesGuide,
  claudeCodeHooksGuide,
  mcpServersClaudeCode,
  specDrivenDevelopment,
  endlessModeExplained,
  persistentMemoryAcrossSessions,
  claudeCodeSettingsReference,
  claudeCodeTaskManagement,
  terminalSetupForClaudeCode,
  selfValidatingAiAgents,
  slashCommandsAndInit,
  worktreeIsolationForFeatures,
  onlineLearningTeachingClaude,
  sandboxingClaudeCode,
  teamVaultSharingAiAssets,
  choosingTheRightClaudeModel,
  context7LibraryDocs,
].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
