#!/usr/bin/env node

/**
 * Keep repository-owned agent instructions portable across Codex and Claude Code.
 *
 * Convention:
 *   AGENTS.md                 canonical shared instructions
 *   CLAUDE.md                 exactly "@AGENTS.md\n"
 *   .agents/skills/<name>/    canonical repository skills
 *   .claude/skills/<name>/    byte-for-byte mirrors of canonical skills
 *
 * Matching target skill directories and tracked mirror-only assets are
 * managed. Untracked or ignored Claude-only skills are deliberately left alone.
 */

import {
  chmod,
  copyFile,
  lstat,
  mkdir,
  readdir,
  readFile,
  rename,
  rmdir,
  unlink,
  writeFile,
} from 'node:fs/promises'
import { constants as fsConstants } from 'node:fs'
import { spawnSync } from 'node:child_process'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const CLAUDE_IMPORT = '@AGENTS.md\n'
const INSTALLED_PATH = path.join('scripts', 'sync-agent-assets.mjs')
const SKILL_NAME_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/
const MAX_SKILL_NAME_LENGTH = 64

class UsageError extends Error {}

function usage() {
  return [
    'Usage:',
    '  sync-agent-assets.mjs --check [--repo <path>]',
    '  sync-agent-assets.mjs --write [--repo <path>]',
    '  sync-agent-assets.mjs --install [--repo <path>]',
  ].join('\n')
}

function parseArgs(argv) {
  let mode = null
  let repo = null

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--check' || arg === '--write' || arg === '--install') {
      if (mode !== null) throw new UsageError('choose exactly one mode')
      mode = arg.slice(2)
      continue
    }
    if (arg === '--repo') {
      index += 1
      if (index >= argv.length || argv[index].startsWith('--')) {
        throw new UsageError('--repo requires a path')
      }
      repo = argv[index]
      continue
    }
    if (arg.startsWith('--repo=')) {
      if (repo !== null) throw new UsageError('--repo may only be provided once')
      repo = arg.slice('--repo='.length)
      if (repo.length === 0) throw new UsageError('--repo requires a path')
      continue
    }
    if (arg === '--help' || arg === '-h') return { help: true }
    throw new UsageError(`unknown argument: ${arg}`)
  }

  if (mode === null) throw new UsageError('a mode is required')
  return { help: false, mode, repo: path.resolve(repo ?? process.cwd()) }
}

async function inspect(candidate) {
  try {
    return await lstat(candidate)
  } catch (error) {
    if (error?.code === 'ENOENT') return null
    throw error
  }
}

function relative(repo, candidate) {
  return path.relative(repo, candidate).split(path.sep).join('/') || '.'
}

function decodeFrontmatterScalar(value, lines, lineIndex, label, field) {
  if (/^[|>][+-]?$/.test(value)) {
    const block = []
    for (let index = lineIndex + 1; index < lines.length; index += 1) {
      const line = lines[index]
      if (line.length > 0 && !/^\s/.test(line)) break
      block.push(line)
    }
    value = block.join('\n').trim()
  } else if (value.startsWith('"')) {
    try {
      value = JSON.parse(value)
    } catch {
      throw new Error(`${label}: SKILL.md frontmatter has an invalid quoted ${field}`)
    }
  } else if (value.startsWith("'")) {
    if (!value.endsWith("'") || value.length < 2) {
      throw new Error(`${label}: SKILL.md frontmatter has an invalid quoted ${field}`)
    }
    value = value.slice(1, -1).replaceAll("''", "'")
  } else {
    value = value.replace(/(^|\s)#.*$/, '').trimEnd()
  }

  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new Error(`${label}: SKILL.md frontmatter ${field} must be a non-empty string`)
  }
  return value
}

function extractFrontmatterMetadata(contents, label) {
  const lines = contents.split(/\r?\n/)
  if (lines[0] !== '---') {
    throw new Error(`${label}: SKILL.md must start with YAML frontmatter`)
  }

  const closing = lines.indexOf('---', 1)
  if (closing === -1) {
    throw new Error(`${label}: SKILL.md frontmatter has no closing --- delimiter`)
  }

  const fields = new Map([
    ['name', []],
    ['description', []],
  ])
  for (let index = 1; index < closing; index += 1) {
    const line = lines[index]
    if (line.includes('\t')) {
      throw new Error(`${label}: SKILL.md frontmatter must not contain tabs`)
    }
    const match = /^(name|description)\s*:\s*(.*?)\s*$/.exec(line)
    if (match) fields.get(match[1]).push({ value: match[2], lineIndex: index })
  }

  if (fields.get('name').length !== 1) {
    throw new Error(`${label}: SKILL.md frontmatter must contain exactly one top-level name field`)
  }
  if (fields.get('description').length !== 1) {
    throw new Error(`${label}: SKILL.md frontmatter must contain exactly one top-level description field`)
  }

  const name = fields.get('name')[0]
  const description = fields.get('description')[0]
  return {
    name: decodeFrontmatterScalar(name.value, lines, name.lineIndex, label, 'name'),
    description: decodeFrontmatterScalar(
      description.value,
      lines,
      description.lineIndex,
      label,
      'description',
    ),
  }
}

function validateSkillName(name, label) {
  if (name.length > MAX_SKILL_NAME_LENGTH || !SKILL_NAME_PATTERN.test(name)) {
    throw new Error(
      `${label}: skill names must be 1-${MAX_SKILL_NAME_LENGTH} lowercase letters, numbers, or single hyphens`,
    )
  }
}

async function discoverSkills(repo) {
  const sourceRoot = path.join(repo, '.agents', 'skills')
  const sourceInfo = await inspect(sourceRoot)
  if (sourceInfo === null || !sourceInfo.isDirectory()) {
    throw new Error('.agents/skills must exist and be a directory')
  }

  const entries = await readdir(sourceRoot, { withFileTypes: true })
  const skills = []
  for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
    if (entry.name.startsWith('.') || !entry.isDirectory()) continue

    const label = `.agents/skills/${entry.name}`
    validateSkillName(entry.name, label)
    const skillRoot = path.join(sourceRoot, entry.name)
    const skillFile = path.join(skillRoot, 'SKILL.md')
    const skillInfo = await inspect(skillFile)
    if (skillInfo === null || !skillInfo.isFile()) {
      throw new Error(`${label}: SKILL.md is required`)
    }

    const { name: declaredName } = extractFrontmatterMetadata(await readFile(skillFile, 'utf8'), label)
    validateSkillName(declaredName, label)
    if (declaredName !== entry.name) {
      throw new Error(`${label}: frontmatter name ${JSON.stringify(declaredName)} must match the directory name`)
    }

    skills.push({ name: entry.name, sourceRoot })
  }
  return skills
}

function runGit(repo, args) {
  const result = spawnSync('git', ['-C', repo, ...args], {
    encoding: null,
    maxBuffer: 16 * 1024 * 1024,
  })
  if (result.error) {
    if (result.error.code === 'ENOENT') {
      throw new Error('git is required to distinguish tracked mirror assets from agent-local skills')
    }
    throw result.error
  }
  return result
}

async function trackedMirrorOnlyAssets(repo, canonicalNames) {
  const worktree = runGit(repo, ['rev-parse', '--is-inside-work-tree'])
  if (worktree.status !== 0) {
    const message = worktree.stderr.toString('utf8').trim()
    if (/not a git repository/i.test(message)) return []
    throw new Error(`git rev-parse failed: ${message}`)
  }

  const tracked = runGit(repo, ['ls-files', '-z', '--', '.claude/skills'])
  if (tracked.status !== 0) {
    throw new Error(`git ls-files failed: ${tracked.stderr.toString('utf8').trim()}`)
  }

  const prefix = '.claude/skills/'
  const assets = []
  for (const candidate of tracked.stdout.toString('utf8').split('\0').filter(Boolean).sort()) {
    const normalized = candidate.split(path.sep).join('/')
    if (!normalized.startsWith(prefix)) continue
    const remainder = normalized.slice(prefix.length)
    const skillName = remainder.split('/')[0]
    if (!skillName || canonicalNames.has(skillName)) continue

    const absolute = path.join(repo, ...normalized.split('/'))
    if ((await inspect(absolute)) !== null) assets.push({ absolute, relative: normalized })
  }
  return assets
}

async function collectTree(root, { rejectSymlinks = false } = {}) {
  const files = new Map()
  const directories = new Set()

  async function visit(current, currentRelative) {
    const entries = await readdir(current, { withFileTypes: true })
    for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
      const absolute = path.join(current, entry.name)
      const itemRelative = currentRelative ? path.join(currentRelative, entry.name) : entry.name
      const normalized = itemRelative.split(path.sep).join('/')
      const info = await lstat(absolute)

      if (info.isSymbolicLink()) {
        if (rejectSymlinks) throw new Error(`${normalized}: symbolic links are not portable skill assets`)
        files.set(normalized, { absolute, info, kind: 'symlink' })
      } else if (info.isDirectory()) {
        directories.add(normalized)
        await visit(absolute, itemRelative)
      } else if (info.isFile()) {
        files.set(normalized, { absolute, info, kind: 'file' })
      } else {
        throw new Error(`${normalized}: unsupported filesystem entry`)
      }
    }
  }

  await visit(root, '')
  return { files, directories }
}

async function compareSkill(repo, name, sourceRoot, targetRoot) {
  const sourceSkill = path.join(sourceRoot, name)
  const targetSkill = path.join(targetRoot, name)
  const issues = []
  const targetInfo = await inspect(targetSkill)
  const sourceTree = await collectTree(sourceSkill, { rejectSymlinks: true })

  if (targetInfo === null || !targetInfo.isDirectory() || targetInfo.isSymbolicLink()) {
    issues.push(`${relative(repo, targetSkill)}: missing mirrored skill directory`)
    return issues
  }

  const targetTree = await collectTree(targetSkill)
  for (const [file, source] of sourceTree.files) {
    const destination = targetTree.files.get(file)
    const label = relative(repo, path.join(targetSkill, file))
    if (destination === undefined || destination.kind !== 'file') {
      issues.push(`${label}: missing mirrored file`)
      continue
    }

    const [sourceBytes, targetBytes] = await Promise.all([
      readFile(source.absolute),
      readFile(destination.absolute),
    ])
    if (!sourceBytes.equals(targetBytes)) issues.push(`${label}: bytes differ`)
    if ((source.info.mode & 0o111) !== (destination.info.mode & 0o111)) {
      issues.push(`${label}: executable bits differ`)
    }
  }

  for (const [file] of targetTree.files) {
    if (!sourceTree.files.has(file)) {
      issues.push(`${relative(repo, path.join(targetSkill, file))}: extra mirrored file`)
    }
  }
  for (const directory of targetTree.directories) {
    if (!sourceTree.directories.has(directory)) {
      issues.push(`${relative(repo, path.join(targetSkill, directory))}: extra mirrored directory`)
    }
  }

  return issues
}

async function audit(repo) {
  const agents = path.join(repo, 'AGENTS.md')
  const agentsInfo = await inspect(agents)
  if (agentsInfo === null || !agentsInfo.isFile() || agentsInfo.isSymbolicLink()) {
    throw new Error('AGENTS.md must exist as the canonical shared instruction file')
  }

  const skills = await discoverSkills(repo)
  const targetRoot = path.join(repo, '.claude', 'skills')
  const issues = []
  const claude = path.join(repo, 'CLAUDE.md')
  const claudeInfo = await inspect(claude)
  if (claudeInfo === null || !claudeInfo.isFile() || claudeInfo.isSymbolicLink()) {
    issues.push('CLAUDE.md: missing; expected exactly @AGENTS.md')
  } else if ((await readFile(claude, 'utf8')) !== CLAUDE_IMPORT) {
    issues.push('CLAUDE.md: content differs; expected exactly @AGENTS.md')
  }

  for (const skill of skills) {
    issues.push(...(await compareSkill(repo, skill.name, skill.sourceRoot, targetRoot)))
  }
  const canonicalNames = new Set(skills.map(skill => skill.name))
  for (const asset of await trackedMirrorOnlyAssets(repo, canonicalNames)) {
    issues.push(`${asset.relative}: tracked mirror-only asset has no canonical .agents/skills source`)
  }
  return { issues, skills }
}

function isTrivialClaude(contents) {
  const meaningful = contents
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)
  return meaningful.length === 0 || (meaningful.length === 1 && meaningful[0] === '@AGENTS.md')
}

async function removeEntry(candidate) {
  const info = await inspect(candidate)
  if (info === null) return
  if (!info.isDirectory() || info.isSymbolicLink()) {
    await unlink(candidate)
    return
  }

  const entries = await readdir(candidate)
  for (const entry of entries) await removeEntry(path.join(candidate, entry))
  await rmdir(candidate)
}

async function atomicCopy(source, destination, mode) {
  await mkdir(path.dirname(destination), { recursive: true })
  const temporary = `${destination}.pilot-sync-${process.pid}-${Math.random().toString(16).slice(2)}`
  try {
    await copyFile(source, temporary, fsConstants.COPYFILE_FICLONE)
    await chmod(temporary, mode & 0o777)
    await rename(temporary, destination)
  } finally {
    try {
      await unlink(temporary)
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error
    }
  }
}

async function syncSkill(name, sourceRoot, targetRoot) {
  const sourceSkill = path.join(sourceRoot, name)
  const targetSkill = path.join(targetRoot, name)
  const targetInfo = await inspect(targetSkill)
  if (targetInfo !== null && (!targetInfo.isDirectory() || targetInfo.isSymbolicLink())) {
    await removeEntry(targetSkill)
  }
  await mkdir(targetSkill, { recursive: true })

  const sourceTree = await collectTree(sourceSkill, { rejectSymlinks: true })
  const targetTree = await collectTree(targetSkill)

  for (const [file, target] of targetTree.files) {
    if (!sourceTree.files.has(file) || target.kind !== 'file') await removeEntry(target.absolute)
  }

  for (const [file, source] of sourceTree.files) {
    const destination = path.join(targetSkill, file)
    const destinationInfo = await inspect(destination)
    if (destinationInfo !== null && (!destinationInfo.isFile() || destinationInfo.isSymbolicLink())) {
      await removeEntry(destination)
    }
    await atomicCopy(source.absolute, destination, source.info.mode)
  }

  const currentTree = await collectTree(targetSkill)
  const extraDirectories = [...currentTree.directories]
    .filter(directory => !sourceTree.directories.has(directory))
    .sort((left, right) => right.split('/').length - left.split('/').length || right.localeCompare(left))
  for (const directory of extraDirectories) await removeEntry(path.join(targetSkill, directory))
}

async function removeTrackedMirrorOnlyAssets(repo, canonicalNames, targetRoot) {
  const assets = await trackedMirrorOnlyAssets(repo, canonicalNames)
  for (const asset of assets) {
    const info = await inspect(asset.absolute)
    if (info !== null && (!info.isDirectory() || info.isSymbolicLink())) await unlink(asset.absolute)
  }

  const parents = new Set()
  for (const asset of assets) {
    let parent = path.dirname(asset.absolute)
    while (parent.startsWith(`${targetRoot}${path.sep}`)) {
      parents.add(parent)
      parent = path.dirname(parent)
    }
  }
  for (const parent of [...parents].sort((left, right) => right.length - left.length)) {
    try {
      await rmdir(parent)
    } catch (error) {
      if (error?.code !== 'ENOENT' && error?.code !== 'ENOTEMPTY' && error?.code !== 'EEXIST') throw error
    }
  }
}

async function write(repo) {
  const agents = path.join(repo, 'AGENTS.md')
  const agentsInfo = await inspect(agents)
  if (agentsInfo === null || !agentsInfo.isFile() || agentsInfo.isSymbolicLink()) {
    throw new Error('AGENTS.md must exist before agent assets can be synchronized')
  }

  const skills = await discoverSkills(repo)
  const claude = path.join(repo, 'CLAUDE.md')
  const claudeInfo = await inspect(claude)
  if (claudeInfo !== null) {
    if (!claudeInfo.isFile() || claudeInfo.isSymbolicLink()) {
      throw new Error('refusing to replace CLAUDE.md because it is not a regular file')
    }
    const contents = await readFile(claude, 'utf8')
    if (!isTrivialClaude(contents)) {
      throw new Error(
        'refusing to overwrite nontrivial CLAUDE.md; move its unique instructions into AGENTS.md first',
      )
    }
  }

  await writeFile(claude, CLAUDE_IMPORT, 'utf8')
  const targetRoot = path.join(repo, '.claude', 'skills')
  await mkdir(targetRoot, { recursive: true })
  for (const skill of skills) await syncSkill(skill.name, skill.sourceRoot, targetRoot)
  await removeTrackedMirrorOnlyAssets(repo, new Set(skills.map(skill => skill.name)), targetRoot)

  const result = await audit(repo)
  if (result.issues.length > 0) {
    throw new Error(`synchronization did not converge:\n${result.issues.map(issue => `- ${issue}`).join('\n')}`)
  }
  return skills.length
}

async function install(repo) {
  const source = fileURLToPath(import.meta.url)
  const destination = path.join(repo, INSTALLED_PATH)
  const repoInfo = await inspect(repo)
  if (repoInfo === null || !repoInfo.isDirectory()) throw new Error(`repository path does not exist: ${repo}`)

  if (path.resolve(source) !== path.resolve(destination)) {
    await atomicCopy(source, destination, 0o755)
  } else {
    await chmod(destination, 0o755)
  }
  return destination
}

function shellQuote(value) {
  if (/^[A-Za-z0-9_./:=+-]+$/.test(value)) return value
  return `'${value.replaceAll("'", "'\\''")}'`
}

function recoveryCommand(repo) {
  return [
    shellQuote(process.execPath),
    shellQuote(fileURLToPath(import.meta.url)),
    '--write',
    '--repo',
    shellQuote(repo),
  ].join(' ')
}

async function main() {
  let options
  try {
    options = parseArgs(process.argv.slice(2))
  } catch (error) {
    if (!(error instanceof UsageError)) throw error
    console.error(`Error: ${error.message}\n\n${usage()}`)
    process.exitCode = 2
    return
  }

  if (options.help) {
    console.log(usage())
    return
  }

  if (options.mode === 'install') {
    const destination = await install(options.repo)
    const count = await write(options.repo)
    console.log(`Installed ${relative(options.repo, destination)}`)
    console.log(`Synchronized CLAUDE.md and ${count} skill${count === 1 ? '' : 's'}.`)
    console.log(`Check: node ${INSTALLED_PATH.split(path.sep).join('/')} --check`)
    return
  }

  if (options.mode === 'write') {
    const count = await write(options.repo)
    console.log(`Synchronized CLAUDE.md and ${count} skill${count === 1 ? '' : 's'}.`)
    return
  }

  const { issues, skills } = await audit(options.repo)
  if (issues.length === 0) {
    console.log(`Agent assets are synchronized (${skills.length} skill${skills.length === 1 ? '' : 's'}).`)
    return
  }

  console.error('Agent asset drift detected:')
  for (const issue of issues) console.error(`- ${issue}`)
  console.error(`Recovery: ${recoveryCommand(options.repo)}`)
  process.exitCode = 1
}

main().catch(error => {
  console.error(`Error: ${error.message}`)
  process.exitCode = 1
})
