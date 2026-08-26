#!/usr/bin/env node

/** Read a scoped dead-code heuristic snapshot from an existing CodeGraph index. */

import { constants as fsConstants } from 'node:fs'
import { accessSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { createRequire } from 'node:module'
import path from 'node:path'
import process from 'node:process'

const DEFAULT_LIMIT = 100
const MAX_LIMIT = 1000
const CODEGRAPH_PACKAGE_NAME = '@colbymchenry/codegraph'

process.env.CODEGRAPH_TELEMETRY = '0'

class UsageError extends Error {}

function usage() {
  return [
    'Usage:',
    '  codegraph-candidates.mjs [--root <path>] [--scope <relative-path>]...',
    '    [--exclude <relative-path>]... [--limit <1-1000>]',
    '',
    'Reads an existing CodeGraph index. It never initializes, indexes, or syncs.',
    'Scopes and exclusions are repository-relative path prefixes.',
  ].join('\n')
}

function optionValue(argv, index, option) {
  const argument = argv[index]
  if (argument === option) {
    const value = argv[index + 1]
    if (value === undefined || value.startsWith('--')) {
      throw new UsageError(`${option} requires a value`)
    }
    return { value, consumed: 2 }
  }
  if (argument.startsWith(`${option}=`)) {
    const value = argument.slice(option.length + 1)
    if (value.length === 0) throw new UsageError(`${option} requires a value`)
    return { value, consumed: 1 }
  }
  return null
}

function parseArgs(argv) {
  let root = null
  let limit = DEFAULT_LIMIT
  let limitSeen = false
  const scopes = []
  const exclusions = []

  for (let index = 0; index < argv.length; ) {
    const argument = argv[index]
    if (argument === '--help' || argument === '-h') return { help: true }

    const rootOption = optionValue(argv, index, '--root')
    if (rootOption !== null) {
      if (root !== null) throw new UsageError('--root may only be provided once')
      root = rootOption.value
      index += rootOption.consumed
      continue
    }

    const scopeOption = optionValue(argv, index, '--scope')
    if (scopeOption !== null) {
      scopes.push(scopeOption.value)
      index += scopeOption.consumed
      continue
    }

    const excludeOption = optionValue(argv, index, '--exclude')
    if (excludeOption !== null) {
      exclusions.push(excludeOption.value)
      index += excludeOption.consumed
      continue
    }

    const limitOption = optionValue(argv, index, '--limit')
    if (limitOption !== null) {
      if (limitSeen) throw new UsageError('--limit may only be provided once')
      limitSeen = true
      limit = Number(limitOption.value)
      if (!Number.isSafeInteger(limit) || limit < 1 || limit > MAX_LIMIT) {
        throw new UsageError(`--limit must be an integer from 1 to ${MAX_LIMIT}`)
      }
      index += limitOption.consumed
      continue
    }

    throw new UsageError(`unknown argument: ${argument}`)
  }

  return { help: false, root: path.resolve(root ?? process.cwd()), scopes, exclusions, limit }
}

function compareText(left, right) {
  if (left < right) return -1
  if (left > right) return 1
  return 0
}

function normalizeFilter(value, label) {
  const normalized = value.replaceAll('\\', '/').replace(/^\.\//, '').replace(/\/$/, '')
  if (normalized === '' || normalized === '.') return ''
  if (normalized.startsWith('/') || /^[A-Za-z]:/.test(normalized)) {
    throw new UsageError(`${label} must be repository-relative: ${value}`)
  }
  const parts = normalized.split('/')
  if (parts.some((part) => part === '' || part === '.' || part === '..')) {
    throw new UsageError(`${label} must be a normalized repository-relative path: ${value}`)
  }
  return parts.join('/')
}

function uniqueSortedFilters(values, label) {
  return [...new Set(values.map((value) => normalizeFilter(value, label)))].sort(compareText)
}

function normalizeCandidatePath(value) {
  if (typeof value !== 'string') return null
  const normalized = value.replaceAll('\\', '/').replace(/^\.\//, '')
  if (normalized === '' || normalized.startsWith('/') || /^[A-Za-z]:/.test(normalized)) return null
  if (normalized.split('/').some((part) => part === '' || part === '.' || part === '..')) return null
  return normalized
}

function hasPrefix(candidate, prefix) {
  return prefix === '' || candidate === prefix || candidate.startsWith(`${prefix}/`)
}

function packageRootFrom(candidate) {
  let current
  try {
    current = realpathSync(candidate)
    if (!statSync(current).isDirectory()) current = path.dirname(current)
  } catch {
    return null
  }

  for (let depth = 0; depth < 8; depth += 1) {
    const manifestPath = path.join(current, 'package.json')
    try {
      const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
      if (manifest?.name === CODEGRAPH_PACKAGE_NAME) return current
    } catch {
      // Continue toward the filesystem root.
    }
    const parent = path.dirname(current)
    if (parent === current) break
    current = parent
  }
  return null
}

function executableCandidates() {
  const suffixes = process.platform === 'win32' ? ['codegraph.cmd', 'codegraph.exe', 'codegraph'] : ['codegraph']
  const candidates = []
  for (const directory of (process.env.PATH ?? '').split(path.delimiter)) {
    if (directory === '') continue
    for (const suffix of suffixes) {
      const candidate = path.join(directory, suffix)
      try {
        accessSync(candidate, fsConstants.X_OK)
        candidates.push(candidate)
      } catch {
        // This PATH entry does not contain an executable CodeGraph launcher.
      }
    }
  }
  return candidates
}

function findCodeGraphPackage() {
  const candidates = [...executableCandidates()]
  for (const moduleRoot of (process.env.NODE_PATH ?? '').split(path.delimiter)) {
    if (moduleRoot !== '') candidates.push(path.join(moduleRoot, '@colbymchenry', 'codegraph'))
  }

  const executablePrefix = path.dirname(path.dirname(realpathSync(process.execPath)))
  candidates.push(path.join(executablePrefix, 'lib', 'node_modules', '@colbymchenry', 'codegraph'))
  candidates.push(path.join(path.dirname(process.execPath), 'node_modules', '@colbymchenry', 'codegraph'))

  for (const candidate of candidates) {
    const packageRoot = packageRootFrom(candidate)
    if (packageRoot !== null) return packageRoot
  }
  throw new Error('globally installed @colbymchenry/codegraph SDK was not found; no installation was attempted')
}

function loadCodeGraphSdk() {
  const packageRoot = findCodeGraphPackage()
  const require = createRequire(import.meta.url)
  const sdk = require(packageRoot)
  if (typeof sdk?.CodeGraph?.open !== 'function') {
    throw new Error(`CodeGraph at ${packageRoot} does not expose the expected read-only SDK`)
  }
  return sdk
}

function inspectIndex(graph) {
  const indexState = typeof graph.getIndexState === 'function' ? graph.getIndexState() : null
  const pendingReferences =
    typeof graph.getPendingReferenceCount === 'function' ? graph.getPendingReferenceCount() : null
  const stale = typeof graph.isIndexStale === 'function' ? graph.isIndexStale() : null
  const warnings = []
  if (indexState !== null && indexState !== 'complete') warnings.push(`index state is ${indexState}`)
  if (pendingReferences !== null && pendingReferences > 0) {
    warnings.push(`index has ${pendingReferences} pending reference(s)`)
  }
  if (stale === true) warnings.push('index was built by an older extraction engine')
  return { indexState, pendingReferences, stale, warnings }
}

function candidateRecord(node) {
  const file = normalizeCandidatePath(node?.filePath)
  if (file === null || typeof node?.name !== 'string' || typeof node?.kind !== 'string') return null
  return {
    file,
    line: Number.isSafeInteger(node.startLine) ? node.startLine : null,
    end_line: Number.isSafeInteger(node.endLine) ? node.endLine : null,
    name: node.name,
    qualified_name: typeof node.qualifiedName === 'string' ? node.qualifiedName : node.name,
    kind: node.kind,
    language: typeof node.language === 'string' ? node.language : 'unknown',
    visibility: typeof node.visibility === 'string' ? node.visibility : null,
    is_exported: node.isExported === true,
    is_test_path: /(^|\/)(tests?|__tests__|fixtures?|examples?|benchmarks?)(\/|$)/i.test(file),
  }
}

function compareCandidates(left, right) {
  return (
    compareText(left.file, right.file) ||
    (left.line ?? Number.MAX_SAFE_INTEGER) - (right.line ?? Number.MAX_SAFE_INTEGER) ||
    compareText(left.name, right.name) ||
    compareText(left.kind, right.kind) ||
    compareText(left.qualified_name, right.qualified_name)
  )
}

async function run(options) {
  const root = realpathSync(options.root)
  if (!statSync(root).isDirectory()) throw new Error(`project root is not a directory: ${root}`)
  const databasePath = path.join(root, '.codegraph', 'codegraph.db')
  try {
    if (!statSync(databasePath).isFile()) throw new Error()
  } catch {
    throw new Error(`existing CodeGraph index not found at ${databasePath}; no initialization was attempted`)
  }

  const scopes = uniqueSortedFilters(options.scopes, '--scope')
  if (scopes.length === 0) scopes.push('')
  const exclusions = uniqueSortedFilters(options.exclusions, '--exclude')
  const sdk = loadCodeGraphSdk()
  const graph = await sdk.CodeGraph.open(root, { sync: false, readOnly: true })

  try {
    const index = inspectIndex(graph)
    const rawCandidates = graph.findDeadCode()
    if (!Array.isArray(rawCandidates)) throw new Error('CodeGraph findDeadCode() returned an invalid result')

    const candidates = rawCandidates
      .map(candidateRecord)
      .filter((candidate) => candidate !== null)
      .filter((candidate) => scopes.some((scope) => hasPrefix(candidate.file, scope)))
      .filter((candidate) => !exclusions.some((exclusion) => hasPrefix(candidate.file, exclusion)))
      .sort(compareCandidates)
    const selected = candidates.slice(0, options.limit)

    return {
      schema_version: 1,
      source: 'codegraph-findDeadCode-heuristic',
      project_root: root,
      read_only: true,
      sync: false,
      scope: scopes.map((scope) => scope || '.'),
      exclusions,
      limit: options.limit,
      matching_candidates: candidates.length,
      returned_candidates: selected.length,
      truncated: candidates.length > selected.length,
      index_state: index.indexState,
      pending_references: index.pendingReferences,
      extraction_stale: index.stale,
      warnings: index.warnings,
      candidates: selected,
    }
  } finally {
    graph.close()
  }
}

async function main() {
  try {
    const options = parseArgs(process.argv.slice(2))
    if (options.help) {
      process.stdout.write(`${usage()}\n`)
      return
    }
    process.stdout.write(`${JSON.stringify(await run(options), null, 2)}\n`)
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    if (error instanceof UsageError) process.stderr.write(`${usage()}\n`)
    process.stderr.write(`${JSON.stringify({ schema_version: 1, error: message }, null, 2)}\n`)
    process.exitCode = error instanceof UsageError ? 2 : 1
  }
}

await main()
