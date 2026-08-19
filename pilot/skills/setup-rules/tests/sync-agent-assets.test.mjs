import assert from 'node:assert/strict'
import {
  chmodSync,
  lstatSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  statSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
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
    const files = Object.fromEntries(
      ['demo-skill/SKILL.md', 'demo-skill/scripts/run.sh']
        .sort()
        .map(relativeAsset => {
          const asset = path.join(repo, '.claude', 'skills', ...relativeAsset.split('/'))
          return [
            relativeAsset,
            {
              sha256: createHash('sha256').update(readFileSync(asset)).digest('hex'),
              executableMode: statSync(asset).mode & 0o111,
            },
          ]
        }),
    )
    writeFileSync(
      path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json'),
      `${JSON.stringify({ version: 1, files }, null, 2)}\n`,
    )
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

function writeRule(repo, relativeRule, contents = '# Rule\n') {
  const destination = path.join(repo, ...relativeRule.split('/'))
  mkdirSync(path.dirname(destination), { recursive: true })
  writeFileSync(destination, contents)
  return destination
}

function appendAgents(repo, contents) {
  const agents = path.join(repo, 'AGENTS.md')
  writeFileSync(agents, readFileSync(agents, 'utf8') + contents)
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

test('tracked Claude-only skill is preserved by default and removed only with explicit migration', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    const tracked = path.join(repo, '.claude', 'skills', 'legacy-skill', 'SKILL.md')
    mkdirSync(path.dirname(tracked), { recursive: true })
    writeFileSync(tracked, 'tracked mirror-only skill\n')
    git(repo, 'add', '.')
    git(
      repo,
      '-c',
      'user.name=Pilot Test',
      '-c',
      'user.email=pilot@example.invalid',
      'commit',
      '-qm',
      'fixture',
    )
    assert.equal(git(repo, 'status', '--porcelain').stdout, '')

    let result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /legacy-skill\/SKILL\.md: tracked mirror-only asset/)

    result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /tracked Claude-only skill requires explicit migration/)
    assert.equal(readFileSync(tracked, 'utf8'), 'tracked mirror-only skill\n')
    assert.equal(git(repo, 'status', '--porcelain').stdout, '')

    result = run(repo, '--write', '--force-migration')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(statOrNull(tracked), null)
  } finally {
    cleanup(repo)
  }
})

test('new tracked Claude-only file inside a canonical skill is preserved and mapped for migration', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    git(repo, 'add', '.')
    git(
      repo,
      '-c',
      'user.name=Pilot Test',
      '-c',
      'user.email=pilot@example.invalid',
      'commit',
      '-qm',
      'baseline',
    )
    const extra = path.join(repo, '.claude', 'skills', 'demo-skill', 'references', 'new.md')
    mkdirSync(path.dirname(extra), { recursive: true })
    writeFileSync(extra, 'tracked Claude-only knowledge\n')
    git(repo, 'add', '.claude/skills/demo-skill/references/new.md')
    git(
      repo,
      '-c',
      'user.name=Pilot Test',
      '-c',
      'user.email=pilot@example.invalid',
      'commit',
      '-qm',
      'add Claude-only file',
    )
    assert.equal(git(repo, 'status', '--porcelain').stdout, '')

    for (const mode of ['--check', '--write', '--install']) {
      const result = run(repo, mode)
      assert.equal(result.status, 1, `${mode}: ${result.stderr}`)
      assert.match(result.stderr, /\.claude\/skills\/demo-skill\/references\/new\.md/)
      assert.match(result.stderr, /\.agents\/skills\/demo-skill\/references\/new\.md/)
      assert.equal(readFileSync(extra, 'utf8'), 'tracked Claude-only knowledge\n')
    }

    const forced = run(repo, '--write', '--force-migration')
    assert.equal(forced.status, 0, forced.stderr)
    assert.equal(statOrNull(extra), null)
  } finally {
    cleanup(repo)
  }
})

test('same-name untracked extras are ignored by check and preserved by write', () => {
  const repo = makeRepo()
  try {
    const local = path.join(repo, '.claude', 'skills', 'demo-skill', 'local-notes.txt')
    writeFileSync(local, 'keep local bytes\n')

    let result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(readFileSync(local, 'utf8'), 'keep local bytes\n')
  } finally {
    cleanup(repo)
  }
})

test('same-path untracked drift fails check and write preserves the local bytes', () => {
  const repo = makeRepo()
  try {
    const localSkill = path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')
    writeFileSync(localSkill, 'local conflicting skill\n')

    let result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /SKILL\.md: bytes differ/)
    result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /local Claude skill migration required/)
    assert.match(result.stderr, /migrate or remove the local asset before syncing/)
    assert.equal(readFileSync(localSkill, 'utf8'), 'local conflicting skill\n')
  } finally {
    cleanup(repo)
  }
})

test('same-path ignored drift is preserved and requires migration', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    writeFileSync(path.join(repo, '.gitignore'), '.claude/skills/demo-skill/\n')
    const localSkill = path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')
    writeFileSync(localSkill, 'ignored conflicting skill\n')

    const result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /local Claude skill migration required/)
    assert.equal(readFileSync(localSkill, 'utf8'), 'ignored conflicting skill\n')
  } finally {
    cleanup(repo)
  }
})

test('same-name untracked skill symlink is preserved with its external sentinel', () => {
  const repo = makeRepo({ mirror: false })
  const external = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-external-'))
  const sentinel = path.join(external, 'sentinel.txt')
  try {
    writeFileSync(sentinel, 'outside local skill bytes\n')
    mkdirSync(path.join(repo, '.claude', 'skills'), { recursive: true })
    symlinkSync(external, path.join(repo, '.claude', 'skills', 'demo-skill'), 'dir')

    const result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /local Claude skill migration required/)
    assert.equal(readFileSync(sentinel, 'utf8'), 'outside local skill bytes\n')
    assert.equal(lstatSync(path.join(repo, '.claude', 'skills', 'demo-skill')).isSymbolicLink(), true)
  } finally {
    cleanup(repo)
    cleanup(external)
  }
})

test('legacy exact mirror without a manifest is claimed deterministically by write', () => {
  const repo = makeRepo()
  try {
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    rmSync(manifest)

    let result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /ownership baseline is missing/)
    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.notEqual(statOrNull(manifest), null)
    result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
  } finally {
    cleanup(repo)
  }
})

test('fresh install baseline allows a canonical edit before any git add', () => {
  const repo = makeRepo({ claude: null, mirror: false })
  try {
    git(repo, 'init', '-q')
    let result = run(repo, '--install')
    assert.equal(result.status, 0, result.stderr)
    const provenanceResult = git(repo, 'rev-parse', '--git-path', 'pilot/sync-agent-assets.json')
    const provenancePath = path.resolve(repo, provenanceResult.stdout.trim())
    assert.notEqual(statOrNull(provenancePath), null)
    const canonical = path.join(repo, '.agents', 'skills', 'demo-skill', 'SKILL.md')
    const mirror = path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')
    writeFileSync(
      canonical,
      '---\nname: demo-skill\ndescription: Edited immediately after setup.\n---\n\n# Fresh update\n',
    )

    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(readFileSync(mirror, 'utf8'), readFileSync(canonical, 'utf8'))
    result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
  } finally {
    cleanup(repo)
  }
})

test('hostile repository manifest cannot authorize overwriting an untracked local mirror', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    const mirror = path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    writeFileSync(mirror, 'hostile-branch target hash sentinel\n')
    const data = JSON.parse(readFileSync(manifest, 'utf8'))
    data.files['demo-skill/SKILL.md'] = {
      sha256: createHash('sha256').update(readFileSync(mirror)).digest('hex'),
      executableMode: statSync(mirror).mode & 0o111,
    }
    writeFileSync(manifest, `${JSON.stringify(data, null, 2)}\n`)

    const result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /untracked or ignored Claude skill conflicts/)
    assert.equal(readFileSync(mirror, 'utf8'), 'hostile-branch target hash sentinel\n')
  } finally {
    cleanup(repo)
  }
})

test('hostile repository manifest cannot authorize deleting an untracked local extra', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    const sentinel = path.join(repo, '.claude', 'skills', 'demo-skill', 'local-sentinel.txt')
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    writeFileSync(sentinel, 'must survive hostile baseline\n')
    const data = JSON.parse(readFileSync(manifest, 'utf8'))
    data.files['demo-skill/local-sentinel.txt'] = {
      sha256: createHash('sha256').update(readFileSync(sentinel)).digest('hex'),
      executableMode: 0,
    }
    writeFileSync(manifest, `${JSON.stringify(data, null, 2)}\n`)

    const result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(readFileSync(sentinel, 'utf8'), 'must survive hostile baseline\n')
  } finally {
    cleanup(repo)
  }
})

test('fresh clone tracked mirrors reconcile without trusted local provenance', () => {
  const repo = makeRepo()
  try {
    git(repo, 'init', '-q')
    git(repo, 'add', 'AGENTS.md', 'CLAUDE.md', '.agents', '.claude')
    const canonical = path.join(repo, '.agents', 'skills', 'demo-skill', 'SKILL.md')
    const mirror = path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')
    writeFileSync(
      canonical,
      '---\nname: demo-skill\ndescription: Fresh clone canonical edit.\n---\n\n# Clone update\n',
    )

    const result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(readFileSync(mirror, 'utf8'), readFileSync(canonical, 'utf8'))
  } finally {
    cleanup(repo)
  }
})

test('both canonical and mirror divergence refuses and preserves the mirror', () => {
  const repo = makeRepo({ claude: null, mirror: false })
  try {
    git(repo, 'init', '-q')
    let result = run(repo, '--install')
    assert.equal(result.status, 0, result.stderr)
    const canonical = path.join(repo, '.agents', 'skills', 'demo-skill', 'SKILL.md')
    const mirror = path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')
    writeFileSync(
      canonical,
      '---\nname: demo-skill\ndescription: Canonical branch.\n---\n\n# Canonical\n',
    )
    writeFileSync(mirror, 'independent mirror branch\n')

    result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /do not have a safe ownership direction/)
    assert.equal(readFileSync(mirror, 'utf8'), 'independent mirror branch\n')
  } finally {
    cleanup(repo)
  }
})

test('tampered but valid manifest fails check and exact trees can refresh it', () => {
  const repo = makeRepo()
  try {
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    const data = JSON.parse(readFileSync(manifest, 'utf8'))
    data.files['demo-skill/SKILL.md'].sha256 = '0'.repeat(64)
    writeFileSync(manifest, `${JSON.stringify(data, null, 2)}\n`)

    let result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /canonical asset diverges from baseline/)
    assert.match(result.stderr, /mirrored asset diverges from baseline/)
    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
  } finally {
    cleanup(repo)
  }
})

test('invalid manifest is refused instead of discarding provenance', () => {
  const repo = makeRepo()
  try {
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    writeFileSync(manifest, '{not json\n')
    const before = readFileSync(path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md'))

    const result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /contains invalid JSON/)
    assert.deepEqual(readFileSync(path.join(repo, '.claude', 'skills', 'demo-skill', 'SKILL.md')), before)
  } finally {
    cleanup(repo)
  }
})

test('recorded stale generated file is removed and dropped from the manifest', () => {
  const repo = makeRepo({ claude: null, mirror: false })
  try {
    git(repo, 'init', '-q')
    let result = run(repo, '--install')
    assert.equal(result.status, 0, result.stderr)
    const canonical = path.join(repo, '.agents', 'skills', 'demo-skill', 'scripts', 'run.sh')
    const mirror = path.join(repo, '.claude', 'skills', 'demo-skill', 'scripts', 'run.sh')
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    rmSync(canonical)

    result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /stale managed file record: demo-skill\/scripts\/run\.sh/)
    result = run(repo, '--write')
    assert.equal(result.status, 0, result.stderr)
    assert.equal(statOrNull(mirror), null)
    assert.equal('demo-skill/scripts/run.sh' in JSON.parse(readFileSync(manifest, 'utf8')).files, false)
    result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
  } finally {
    cleanup(repo)
  }
})

test('edited stale generated file is preserved when canonical deletes it', () => {
  const repo = makeRepo({ claude: null, mirror: false })
  try {
    git(repo, 'init', '-q')
    let result = run(repo, '--install')
    assert.equal(result.status, 0, result.stderr)
    const canonical = path.join(repo, '.agents', 'skills', 'demo-skill', 'scripts', 'run.sh')
    const mirror = path.join(repo, '.claude', 'skills', 'demo-skill', 'scripts', 'run.sh')
    rmSync(canonical)
    writeFileSync(mirror, '#!/bin/sh\necho locally edited\n')

    result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /do not have a safe ownership direction/)
    assert.equal(readFileSync(mirror, 'utf8'), '#!/bin/sh\necho locally edited\n')
  } finally {
    cleanup(repo)
  }
})

test('check accepts exact root and nested rule routes while README remains optional', () => {
  const repo = makeRepo()
  try {
    writeRule(repo, '.claude/rules/project.md')
    writeRule(repo, '.claude/rules/product/testing.md')
    writeRule(repo, '.claude/rules/README.md', '# Rule index\n')
    appendAgents(
      repo,
      '\n- `.claude/rules/project.md` — project guidance\n- `.claude/rules/product/testing.md` — test guidance\n',
    )

    const result = run(repo, '--check')
    assert.equal(result.status, 0, result.stderr)
  } finally {
    cleanup(repo)
  }
})

test('new rule fails until AGENTS.md gains its exact path and write never invents the route', () => {
  const repo = makeRepo()
  try {
    writeRule(repo, '.claude/rules/new-rule.md')
    const before = readFileSync(path.join(repo, 'AGENTS.md'), 'utf8')

    let result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /AGENTS\.md is missing exact rule reference: \.claude\/rules\/new-rule\.md/)

    result = run(repo, '--write')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /rule routing parity failed/)
    assert.equal(readFileSync(path.join(repo, 'AGENTS.md'), 'utf8'), before)
  } finally {
    cleanup(repo)
  }
})

test('nested rule basename is not a substitute for its exact repository-relative route', () => {
  const repo = makeRepo()
  try {
    writeRule(repo, '.claude/rules/product/exact-path.md')
    appendAgents(repo, '\n- `exact-path.md` — incomplete route\n')

    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(
      result.stderr,
      /AGENTS\.md is missing exact rule reference: \.claude\/rules\/product\/exact-path\.md/,
    )
  } finally {
    cleanup(repo)
  }
})

test('renamed rule reports both its missing new route and stale previous route', () => {
  const repo = makeRepo()
  try {
    writeRule(repo, '.claude/rules/current-name.md')
    appendAgents(repo, '\n- `.claude/rules/previous-name.md` — renamed guidance\n')

    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /missing exact rule reference: \.claude\/rules\/current-name\.md/)
    assert.match(result.stderr, /references missing rule file: \.claude\/rules\/previous-name\.md/)
  } finally {
    cleanup(repo)
  }
})

test('stale AGENTS.md rule reference fails when no corresponding file exists', () => {
  const repo = makeRepo()
  try {
    appendAgents(repo, '\n- `.claude/rules/deleted-rule.md` — stale guidance\n')

    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /AGENTS\.md references missing rule file: \.claude\/rules\/deleted-rule\.md/)
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
    git(repo, 'init', '-q')
    const extra = path.join(repo, '.claude', 'skills', 'demo-skill', 'stale', 'extra.txt')
    mkdirSync(path.dirname(extra), { recursive: true })
    writeFileSync(extra, 'stale\n')
    git(repo, 'add', '.claude/skills/demo-skill')
    const result = run(repo, '--check')
    assert.equal(result.status, 1)
    assert.match(result.stderr, /extra\.txt: extra tracked mirrored file/)
    assert.match(result.stderr, /stale: extra tracked mirrored directory/)
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

test('all modes reject a symlinked .claude/skills root without touching its target', () => {
  const repo = makeRepo()
  const external = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-external-'))
  const sentinel = path.join(external, 'sentinel.txt')
  try {
    writeFileSync(sentinel, 'outside bytes\n')
    rmSync(path.join(repo, '.claude', 'skills'), { recursive: true })
    symlinkSync(external, path.join(repo, '.claude', 'skills'), 'dir')

    for (const mode of ['--check', '--write', '--install']) {
      const result = run(repo, mode)
      assert.equal(result.status, 1, `${mode}: ${result.stderr}`)
      assert.match(result.stderr, /refusing symlinked repository path: \.claude\/skills/)
      assert.equal(readFileSync(sentinel, 'utf8'), 'outside bytes\n')
    }
    assert.equal(statOrNull(path.join(repo, 'scripts', 'sync-agent-assets.mjs')), null)
  } finally {
    cleanup(repo)
    cleanup(external)
  }
})

test('all modes reject a symlinked .claude root without touching its target', () => {
  const repo = makeRepo({ mirror: false })
  const external = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-external-'))
  const sentinel = path.join(external, 'sentinel.txt')
  try {
    writeFileSync(sentinel, 'outside bytes\n')
    symlinkSync(external, path.join(repo, '.claude'), 'dir')

    for (const mode of ['--check', '--write', '--install']) {
      const result = run(repo, mode)
      assert.equal(result.status, 1, `${mode}: ${result.stderr}`)
      assert.match(result.stderr, /refusing symlinked repository path: \.claude/)
      assert.equal(readFileSync(sentinel, 'utf8'), 'outside bytes\n')
    }
    assert.equal(statOrNull(path.join(repo, 'scripts', 'sync-agent-assets.mjs')), null)
  } finally {
    cleanup(repo)
    cleanup(external)
  }
})

test('all modes reject a symlinked .claude/rules root without touching its target', () => {
  const repo = makeRepo()
  const external = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-external-'))
  const sentinel = path.join(external, 'sentinel.txt')
  try {
    writeFileSync(sentinel, 'outside bytes\n')
    symlinkSync(external, path.join(repo, '.claude', 'rules'), 'dir')

    for (const mode of ['--check', '--write', '--install']) {
      const result = run(repo, mode)
      assert.equal(result.status, 1, `${mode}: ${result.stderr}`)
      assert.match(result.stderr, /refusing symlinked repository path: \.claude\/rules/)
      assert.equal(readFileSync(sentinel, 'utf8'), 'outside bytes\n')
    }
    assert.equal(statOrNull(path.join(repo, 'scripts', 'sync-agent-assets.mjs')), null)
  } finally {
    cleanup(repo)
    cleanup(external)
  }
})

test('all modes reject symlinked canonical skill roots', () => {
  for (const repositoryPath of ['.agents', '.agents/skills']) {
    const repo = makeRepo()
    const external = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-external-'))
    const sentinel = path.join(external, 'sentinel.txt')
    try {
      writeFileSync(sentinel, 'outside bytes\n')
      const candidate = path.join(repo, ...repositoryPath.split('/'))
      rmSync(candidate, { recursive: true })
      symlinkSync(external, candidate, 'dir')

      for (const mode of ['--check', '--write', '--install']) {
        const result = run(repo, mode)
        assert.equal(result.status, 1, `${repositoryPath} ${mode}: ${result.stderr}`)
        assert.ok(result.stderr.includes(`refusing symlinked repository path: ${repositoryPath}`))
        assert.equal(readFileSync(sentinel, 'utf8'), 'outside bytes\n')
      }
    } finally {
      cleanup(repo)
      cleanup(external)
    }
  }
})

test('install rejects a symlinked scripts destination without touching its target', () => {
  const repo = makeRepo()
  const external = mkdtempSync(path.join(tmpdir(), 'pilot-agent-assets-external-'))
  const sentinel = path.join(external, 'sentinel.txt')
  try {
    writeFileSync(sentinel, 'outside bytes\n')
    symlinkSync(external, path.join(repo, 'scripts'), 'dir')

    const result = run(repo, '--install')
    assert.equal(result.status, 1, result.stderr)
    assert.match(result.stderr, /refusing symlinked repository path: scripts/)
    assert.equal(readFileSync(sentinel, 'utf8'), 'outside bytes\n')
    assert.equal(statOrNull(path.join(external, 'sync-agent-assets.mjs')), null)
  } finally {
    cleanup(repo)
    cleanup(external)
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

    result = run(repo, '--check', '--force-migration')
    assert.equal(result.status, 2)
    assert.match(result.stderr, /only valid with --write or --install/)
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

test('write applies canonical drift, removes managed extras, preserves unmanaged skills, and converges', () => {
  const repo = makeRepo({ claude: '  @AGENTS.md\r\n' })
  try {
    git(repo, 'init', '-q')
    const source = path.join(repo, '.agents', 'skills', 'demo-skill')
    const target = path.join(repo, '.claude', 'skills', 'demo-skill')
    writeFileSync(
      path.join(source, 'SKILL.md'),
      '---\nname: demo-skill\ndescription: Canonical update.\n---\n\n# Updated demo\n',
    )
    chmodSync(path.join(source, 'scripts', 'run.sh'), 0o644)
    writeFileSync(path.join(target, 'extra.txt'), 'remove me\n')
    const manifest = path.join(repo, '.claude', 'skills', '.pilot-sync-manifest.json')
    const manifestData = JSON.parse(readFileSync(manifest, 'utf8'))
    manifestData.files['demo-skill/extra.txt'] = {
      sha256: createHash('sha256').update(readFileSync(path.join(target, 'extra.txt'))).digest('hex'),
      executableMode: 0,
    }
    writeFileSync(manifest, `${JSON.stringify(manifestData, null, 2)}\n`)
    git(repo, 'add', '.claude/skills/demo-skill')
    const unmanaged = path.join(repo, '.claude', 'skills', 'private-skill', 'notes.txt')
    mkdirSync(path.dirname(unmanaged), { recursive: true })
    writeFileSync(unmanaged, 'keep me\n')

    const written = run(repo, '--write')
    assert.equal(written.status, 0, written.stderr)
    assert.equal(readFileSync(path.join(repo, 'CLAUDE.md'), 'utf8'), '@AGENTS.md\n')
    assert.equal(readFileSync(path.join(target, 'SKILL.md'), 'utf8'), readFileSync(path.join(source, 'SKILL.md'), 'utf8'))
    assert.equal(statSync(path.join(target, 'scripts', 'run.sh')).mode & 0o111, 0)
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
