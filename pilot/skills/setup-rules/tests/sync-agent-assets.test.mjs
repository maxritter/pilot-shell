import assert from 'node:assert/strict'
import { chmodSync, mkdtempSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const SCRIPT = path.resolve(HERE, '..', 'scripts', 'sync-agent-assets.mjs')

function makeRepo({ claude = '@AGENTS.md\n', mirror = true } = {}) {
  const repo = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-'))
  writeFileSync(path.join(repo, 'AGENTS.md'), '# Shared instructions\n')
  if (claude !== null) writeFileSync(path.join(repo, 'CLAUDE.md'), claude)

  const source = path.join(repo, '.agents', 'skills', 'demo-skill')
  mkdirSync(path.join(source, 'scripts'), { recursive: true })
  writeFileSync(
    path.join(source, 'SKILL.md'),
    '---\nname: demo-skill\ndescription: Demonstrates repository skills.\n---\n\n# Demo\n',
  )
  writeFileSync(path.join(source, 'scripts', 'run.sh'), '#!/bin/sh\necho demo\n')
  chmodSync(path.join(source, 'scripts', 'run.sh'), 0o755)

  if (mirror) {
    const target = path.join(repo, '.claude', 'skills', 'demo-skill')
    mkdirSync(path.join(target, 'scripts'), { recursive: true })
    writeFileSync(path.join(target, 'SKILL.md'), readFileSync(path.join(source, 'SKILL.md')))
    writeFileSync(path.join(target, 'scripts', 'run.sh'), readFileSync(path.join(source, 'scripts', 'run.sh')))
    chmodSync(path.join(target, 'scripts', 'run.sh'), 0o755)
  }
  return repo
}

function run(repo, ...args) {
  return spawnSync(process.execPath, [SCRIPT, ...args, '--repo', repo], {
    cwd: repo,
    encoding: 'utf8',
  })
}

function git(repo, ...args) {
  const result = spawnSync('git', args, { cwd: repo, encoding: 'utf8' })
  assert.equal(result.status, 0, result.stderr)
  return result
}

function cleanup(repo) {
  rmSync(repo, { recursive: true, force: true })
}

test('check accepts an exact mirror and ignores unrelated Claude skills', () => {
  const repo = makeRepo()
  try {
    const unmanaged = path.join(repo, '.claude', 'skills', 'local-only', 'SKILL.md')
    mkdirSync(path.dirname(unmanaged), { recursive: true })
    writeFileSync(unmanaged, 'local and unmanaged\n')

    const result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
    assert.match(result.stdout, /Agent assets are synchronized/)
    assert.equal(readFileSync(unmanaged, 'utf8'), 'local and unmanaged\n')
  } finally {
    cleanup(repo)
  }
})

test('check preserves untracked and ignored Claude-only skills in a Git repository', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    writeFileSync(path.join(repo, '.gitignore'), '.claude/skills/ignored-skill/\n')
    const untracked = path.join(repo, '.claude', 'skills', 'local-skill', 'SKILL.md')
    const ignored = path.join(repo, '.claude', 'skills', 'ignored-skill', 'SKILL.md')
    mkdirSync(path.dirname(untracked), { recursive: true })
    mkdirSync(path.dirname(ignored), { recursive: true })
    writeFileSync(untracked, 'untracked\n')
    writeFileSync(ignored, 'ignored\n')

    let result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(readFileSync(untracked, 'utf8'), 'untracked\n')
    assert.equal(readFileSync(ignored, 'utf8'), 'ignored\n')
  } finally {
    cleanup(repo)
  }
})

test('tracked Claude-only skill assets fail parity and write removes only the tracked asset', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    const tracked = path.join(repo, '.claude', 'skills', 'legacy-skill', 'SKILL.md')
    const local = path.join(repo, '.claude', 'skills', 'legacy-skill', 'local-notes.txt')
    mkdirSync(path.dirname(tracked), { recursive: true })
    writeFileSync(tracked, 'tracked mirror-only skill\n')
    writeFileSync(local, 'untracked local notes\n')
    git(repo, 'add', '.claude/skills/legacy-skill/SKILL.md')

    let result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /legacy-skill\/SKILL\.md: tracked mirror-only asset/)

    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(statOrNull(tracked), null)
    assert.equal(readFileSync(local, 'utf8'), 'untracked local notes\n')
  } finally {
    cleanup(repo)
  }
})

test('check reports byte drift with an exact recovery command', () => {
  const repo = makeRepo()
  try {
    writeFileSync(path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md'), 'drift\n')
    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /SKILL\.md: bytes differ/)
    const recovery = result.stderr.match(/^Recovery: (.+)$/m)?.[1]
    assert.ok(recovery, result.stderr)
    assert.match(recovery, /--write --repo/)
  } finally {
    cleanup(repo)
  }
})

test('check reports missing mirror files and CLAUDE.md', () => {
  const repo = makeRepo({ claude: null })
  try {
    rmSync(path.join(repo, '.claude', 'skills', 'demo-skill', 'scripts', 'run.sh'))
    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /CLAUDE\.md: missing/)
    assert.match(result.stderr, /run\.sh: missing mirrored file/)
  } finally {
    cleanup(repo)
  }
})

test('check reports extra entries inside a managed mirrored skill', () => {
  const repo = makeRepo()
  try {
    const extra = path.join(repo, '.claude', 'skills', 'demo-skill', 'stale', 'extra.txt')
    mkdirSync(path.dirname(extra), { recursive: true })
    writeFileSync(extra, 'stale\n')
    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /extra\.txt: extra mirrored file/)
    assert.match(result.stderr, /stale: extra mirrored directory/)
  } finally {
    cleanup(repo)
  }
})

test('check compares executable bits', () => {
  const repo = makeRepo()
  try {
    chmodSync(path.join(repo, '.claude', 'skills', 'demo-skill', 'scripts', 'run.sh'), 0o644)
    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /run\.sh: executable bits differ/)
  } finally {
    cleanup(repo)
  }
})

test('CLI requires exactly one explicit mode', () => {
  const repo = makeRepo()
  try {
    let result = run(repo)
    assert.equal(result.status, 2)
    assert.match(result.stderr, /a mode is required/)

    result = run(repo, '--check', '--write')
    assert.equal(result.status, 2)
    assert.match(result.stderr, /choose exactly one mode/)
  } finally {
    cleanup(repo)
  }
})

test('invalid skill frontmatter and name mismatch fail before writes', () => {
  const repo = makeRepo({ claude: null, mirror: false })
  try {
    const skill = path.join(repo, '.agents', 'skills', 'demo-skill', 'SKILL.md')
    writeFileSync(skill, '# no frontmatter\n')
    let result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /must start with YAML frontmatter/)
    assert.equal(statOrNull(path.join(repo, 'CLAUDE.md')), null)

    writeFileSync(skill, '---\nname: demo-skill\n---\n\n# Demo\n')
    result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /exactly one top-level description field/)

    writeFileSync(skill, '---\nname: demo-skill\ndescription: # empty comment\n---\n\n# Demo\n')
    result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /description must be a non-empty string/)

    writeFileSync(skill, '---\nname: another-skill\ndescription: Wrong name.\n---\n\n# Demo\n')
    result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /must match the directory name/)
  } finally {
    cleanup(repo)
  }
})

test('write repairs drift, removes managed extras, preserves unmanaged skills, and converges', () => {
  const repo = makeRepo({ claude: '  @AGENTS.md\r\n' })
  try {
    const target = path.join(repo, '.claude', 'skills', 'demo-skill')
    writeFileSync(path.join(target, 'SKILL.md'), 'drift\n')
    chmodSync(path.join(target, 'scripts', 'run.sh'), 0o644)
    writeFileSync(path.join(target, 'extra.txt'), 'remove me\n')
    const unmanaged = path.join(repo, '.claude', 'skills', 'private-skill', 'notes.txt')
    mkdirSync(path.dirname(unmanaged), { recursive: true })
    writeFileSync(unmanaged, 'keep me\n')

    const written = run(repo, '--write')
    assert.equal(written.status, 0, written.stderr)
    assert.equal(readFileSync(path.join(repo, 'CLAUDE.md'), 'utf8'), '@AGENTS.md\n')
    assert.equal(readFileSync(path.join(target, 'SKILL.md'), 'utf8'), readFileSync(path.join(repo, '.agents', 'skills', 'demo-skill', 'SKILL.md'), 'utf8'))
    assert.equal(statSync(path.join(target, 'scripts', 'run.sh')).mode & 0o111, 0o111)
    assert.equal(statOrNull(path.join(target, 'extra.txt')), null)
    assert.equal(readFileSync(unmanaged, 'utf8'), 'keep me\n')

    const checked = run(repo, '--check')
    assert.equal(checked.status, 0, checked.stderr)
  } finally {
    cleanup(repo)
  }
})

test('write refuses to overwrite a nontrivial CLAUDE.md', () => {
  const repo = makeRepo({ claude: '# Claude-only instructions\n' })
  try {
    const result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /refusing to overwrite nontrivial CLAUDE\.md/)
    assert.equal(readFileSync(path.join(repo, 'CLAUDE.md'), 'utf8'), '# Claude-only instructions\n')
  } finally {
    cleanup(repo)
  }
})

test('install writes an executable standalone copy and converges the repository', () => {
  const repo = makeRepo({ claude: null, mirror: false })
  try {
    const result = run(repo, '--install')
    assert.equal(result.status, 0, result.stderr)
    const installed = path.join(repo, 'scripts', 'sync-agent-assets.mjs')
    assert.deepEqual(readFileSync(installed), readFileSync(SCRIPT))
    assert.notEqual(statSync(installed).mode & 0o111, 0)
    assert.equal(readFileSync(path.join(repo, 'CLAUDE.md'), 'utf8'), '@AGENTS.md\n')
    assert.equal(
      readFileSync(path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md'), 'utf8'),
      readFileSync(path.join(repo, '.agents', 'skills', 'demo-skill', 'SKILL.md'), 'utf8'),
    )

    const standalone = spawnSync(process.execPath, [installed, '--check'], {
      cwd: repo,
      encoding: 'utf8',
    })
    assert.equal(standalone.status, 0, standalone.stderr)
  } finally {
    cleanup(repo)
  }
})

test('install refuses to converge across a nontrivial CLAUDE.md', () => {
  const repo = makeRepo({ claude: '# Preserve this\n', mirror: false })
  try {
    const result = run(repo, '--install')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /refusing to overwrite nontrivial CLAUDE\.md/)
    assert.equal(readFileSync(path.join(repo, 'CLAUDE.md'), 'utf8'), '# Preserve this\n')
    assert.equal(statOrNull(path.join(repo, '.claude', 'skills', 'demo-skill')), null)
  } finally {
    cleanup(repo)
  }
})

function statOrNull(candidate) {
  try {
    return statSync(candidate)
  } catch (error) {
    if (error?.code === 'ENOENT') return null
    throw error
  }
}
