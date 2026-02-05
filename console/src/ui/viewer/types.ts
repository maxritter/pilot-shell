export interface Observation {
  id: number;
  memory_session_id: string;
  project: string;
  type: string;
  title: string | null;
  subtitle: string | null;
  narrative: string | null;
  text: string | null;
  facts: string | null;
  concepts: string | null;
  files_read: string | null;
  files_modified: string | null;
  prompt_number: number | null;
  created_at: string;
  created_at_epoch: number;
}

export interface Summary {
  id: number;
  session_id: string;
  project: string;
  request?: string;
  investigated?: string;
  learned?: string;
  completed?: string;
  next_steps?: string;
  created_at_epoch: number;
}

export interface UserPrompt {
  id: number;
  content_session_id: string;
  project: string;
  prompt_number: number;
  prompt_text: string;
  created_at_epoch: number;
}

export type FeedItem =
  | (Observation & { itemType: 'observation' })
  | (Summary & { itemType: 'summary' })
  | (UserPrompt & { itemType: 'prompt' });

export interface StreamEvent {
  type: 'initial_load' | 'new_observation' | 'new_summary' | 'new_prompt' | 'processing_status';
  observations?: Observation[];
  summaries?: Summary[];
  prompts?: UserPrompt[];
  projects?: string[];
  observation?: Observation;
  summary?: Summary;
  prompt?: UserPrompt;
  isProcessing?: boolean;
  queueDepth?: number;
}

export interface Settings {
  CLAUDE_PILOT_MODEL: string;
  CLAUDE_PILOT_CONTEXT_OBSERVATIONS: string;
  CLAUDE_PILOT_WORKER_PORT: string;
  CLAUDE_PILOT_WORKER_HOST: string;
  CLAUDE_PILOT_WORKER_BIND?: string;

  CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS?: string;
  CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS?: string;
  CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT?: string;
  CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT?: string;

  CLAUDE_PILOT_CONTEXT_OBSERVATION_TYPES?: string;
  CLAUDE_PILOT_CONTEXT_OBSERVATION_CONCEPTS?: string;

  CLAUDE_PILOT_CONTEXT_FULL_COUNT?: string;
  CLAUDE_PILOT_CONTEXT_FULL_FIELD?: string;
  CLAUDE_PILOT_CONTEXT_SESSION_COUNT?: string;

  CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY?: string;
  CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE?: string;

  CLAUDE_PILOT_SKIP_TOOLS?: string;
  CLAUDE_PILOT_LOG_LEVEL?: string;
  CLAUDE_PILOT_MODE?: string;
  CLAUDE_PILOT_FOLDER_MD_EXCLUDE?: string;
}

export interface WorkerStats {
  version?: string;
  uptime?: number;
  activeSessions?: number;
  sseClients?: number;
}

export interface DatabaseStats {
  size?: number;
  observations?: number;
  sessions?: number;
  summaries?: number;
}

export interface Stats {
  worker?: WorkerStats;
  database?: DatabaseStats;
}
