/**
 * VectorSyncFactory - Creates appropriate vector sync implementation
 *
 * Based on settings, returns ChromaSync or NoopVectorSync.
 * Provides abstraction layer for vector database selection.
 */

import { IVectorSync } from './IVectorSync.js';
import { ChromaSync } from './ChromaSync.js';
import { NoopVectorSync } from './NoopVectorSync.js';
import { SettingsDefaultsManager } from '../../shared/SettingsDefaultsManager.js';
import { USER_SETTINGS_PATH } from '../../shared/paths.js';
import { logger } from '../../utils/logger.js';

export type VectorDbBackend = 'chroma' | 'none' | 'disabled';

/**
 * Create a VectorSync instance based on settings
 * @param project - Project name for collection naming
 * @returns IVectorSync implementation (ChromaSync or NoopVectorSync)
 */
export function createVectorSync(project: string): IVectorSync {
  const settings = SettingsDefaultsManager.loadFromFile(USER_SETTINGS_PATH);
  const isWindows = process.platform === 'win32';

  const chromaEnabled = settings.CLAUDE_PILOT_CHROMA_ENABLED;
  if (!chromaEnabled) {
    logger.info('VECTOR_SYNC', 'Vector database disabled by setting', { project });
    return new NoopVectorSync(project);
  }

  const backend = (settings.CLAUDE_PILOT_VECTOR_DB || 'chroma') as VectorDbBackend;

  if (backend === 'none' || backend === 'disabled') {
    logger.info('VECTOR_SYNC', 'Vector database disabled via CLAUDE_PILOT_VECTOR_DB setting', { project, backend });
    return new NoopVectorSync(project);
  }

  if (isWindows && backend === 'chroma') {
    logger.warn('VECTOR_SYNC', 'Chroma disabled on Windows to prevent console popups. Disable vector DB in settings.', { project });
    return new NoopVectorSync(project);
  }

  logger.info('VECTOR_SYNC', 'Creating vector sync', { project, backend });

  return new ChromaSync(project);
}

/**
 * Check if vector sync is available (for graceful degradation)
 */
export async function isVectorSyncAvailable(sync: IVectorSync): Promise<boolean> {
  try {
    return await sync.isHealthy();
  } catch {
    return false;
  }
}

/**
 * Get the currently configured vector database backend
 */
export function getVectorDbBackend(): VectorDbBackend {
  const settings = SettingsDefaultsManager.loadFromFile(USER_SETTINGS_PATH);
  return (settings.CLAUDE_PILOT_VECTOR_DB || 'chroma') as VectorDbBackend;
}
