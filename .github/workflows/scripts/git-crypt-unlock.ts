// Unlock a git-crypt checkout without git-crypt, in one process.
//
//   bun git-crypt-unlock.ts <key file>     unlock the repository in the current directory
//   bun git-crypt-unlock.ts filter         (run by git) the filter for every encrypted file
//
// `git-crypt unlock` checks out every encrypted file through its own smudge filter, one process per
// file. On a Windows runner, under msys2, that is three to seven minutes for this repository. Here
// git talks to one long-running filter process (gitattributes "filter.<driver>.process") that
// decrypts and encrypts exactly as git-crypt does: AES-256-CTR, the nonce is the first 12 bytes of
// the plaintext's HMAC-SHA1, and every file is checked against that nonce after decryption.
import { createCipheriv, createDecipheriv, createHmac, timingSafeEqual } from "node:crypto"
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs"
import { join, resolve } from "node:path"

const HEADER = Buffer.from("\0GITCRYPT\0", "latin1")
const NONCE_LEN = 12

type Key = { aes: Buffer; hmac: Buffer }

/** The newest key entry of a git-crypt key file (format version 2). */
function loadKey(path: string): Key {
  const data = readFileSync(path)
  let at = 0
  const u32 = () => {
    if (at + 4 > data.length) throw new Error("truncated git-crypt key file")
    const value = data.readUInt32BE(at)
    at += 4
    return value
  }
  const take = (length: number) => {
    if (at + length > data.length) throw new Error("truncated git-crypt key file")
    const value = data.subarray(at, at + length)
    at += length
    return value
  }
  if (!take(12).equals(Buffer.from("\0GITCRYPTKEY", "latin1"))) throw new Error("not a git-crypt key file")
  if (u32() !== 2) throw new Error("unsupported git-crypt key file version")
  for (;;) {
    const field = u32()
    if (field === 0) break
    const length = u32()
    if (field !== 1 && (field & 1) === 1) throw new Error(`unknown critical key header field ${field}`)
    take(length)
  }
  let newest: (Key & { version: number }) | null = null
  while (at < data.length) {
    let version = 0
    let aes: Buffer | null = null
    let hmac: Buffer | null = null
    for (;;) {
      const field = u32()
      if (field === 0) break
      const length = u32()
      if (field === 1 && length === 4) version = take(4).readUInt32BE(0)
      else if (field === 3 && length === 32) aes = Buffer.from(take(32))
      else if (field === 5 && length === 64) hmac = Buffer.from(take(64))
      else if ((field & 1) === 1) throw new Error(`unknown critical key entry field ${field}`)
      else take(length)
    }
    if (aes === null || hmac === null) throw new Error("incomplete git-crypt key entry")
    if (newest === null || version > newest.version) newest = { version, aes, hmac }
  }
  if (newest === null) throw new Error("the git-crypt key file holds no key")
  return newest
}

function ctr(key: Key, nonce: Buffer, decrypt: boolean) {
  const iv = Buffer.concat([nonce, Buffer.alloc(4)])
  return decrypt ? createDecipheriv("aes-256-ctr", key.aes, iv) : createCipheriv("aes-256-ctr", key.aes, iv)
}

function encrypt(key: Key, plain: Buffer): Buffer {
  const nonce = createHmac("sha1", key.hmac).update(plain).digest().subarray(0, NONCE_LEN)
  const cipher = ctr(key, nonce, false)
  return Buffer.concat([HEADER, nonce, cipher.update(plain), cipher.final()])
}

function decrypt(key: Key, stored: Buffer, path: string): Buffer {
  // git-crypt leaves a file that is not encrypted (committed before the attribute) as it is.
  if (stored.length < HEADER.length + NONCE_LEN || !stored.subarray(0, HEADER.length).equals(HEADER))
    return stored
  const nonce = stored.subarray(HEADER.length, HEADER.length + NONCE_LEN)
  const decipher = ctr(key, nonce, true)
  const plain = Buffer.concat([decipher.update(stored.subarray(HEADER.length + NONCE_LEN)), decipher.final()])
  const check = createHmac("sha1", key.hmac).update(plain).digest().subarray(0, NONCE_LEN)
  if (!timingSafeEqual(check, nonce)) throw new Error(`${path}: the git-crypt key does not match`)
  return plain
}

// ---- git's long-running filter protocol (pkt-line) ----

class Packets {
  private buffer = Buffer.alloc(0)
  private reader = Bun.stdin.stream().getReader()
  private async fill(length: number): Promise<boolean> {
    while (this.buffer.length < length) {
      const { value, done } = await this.reader.read()
      if (done) return false
      this.buffer = Buffer.concat([this.buffer, Buffer.from(value)])
    }
    return true
  }
  /** One packet's payload, null for a flush packet, undefined at the end of input. */
  async read(): Promise<Buffer | null | undefined> {
    if (!(await this.fill(4))) return undefined
    const length = Number.parseInt(this.buffer.subarray(0, 4).toString("latin1"), 16)
    if (length === 0) {
      this.buffer = this.buffer.subarray(4)
      return null
    }
    if (!(await this.fill(length))) throw new Error("truncated packet")
    const payload = this.buffer.subarray(4, length)
    this.buffer = this.buffer.subarray(length)
    return payload
  }
  async lines(): Promise<string[] | undefined> {
    const lines: string[] = []
    for (;;) {
      const packet = await this.read()
      if (packet === undefined) return lines.length === 0 ? undefined : lines
      if (packet === null) return lines
      lines.push(packet.toString("utf8").replace(/\n$/, ""))
    }
  }
  async content(): Promise<Buffer> {
    const parts: Buffer[] = []
    for (;;) {
      const packet = await this.read()
      if (packet === undefined) throw new Error("content ended without a flush packet")
      if (packet === null) return Buffer.concat(parts)
      parts.push(Buffer.from(packet))
    }
  }
}

const out: Buffer[] = []
const packet = (payload: Buffer | string) => {
  const data = typeof payload === "string" ? Buffer.from(payload, "utf8") : payload
  out.push(Buffer.from((data.length + 4).toString(16).padStart(4, "0"), "latin1"), data)
}
const flush = () => out.push(Buffer.from("0000", "latin1"))
async function send(): Promise<void> {
  const data = Buffer.concat(out.splice(0))
  await Bun.write(Bun.stdout, data)
}

async function filter(key: Key): Promise<void> {
  const input = new Packets()
  const hello = await input.lines()
  if (hello?.[0] !== "git-filter-client" || !hello.includes("version=2")) throw new Error("not a git filter client")
  packet("git-filter-server\n")
  packet("version=2\n")
  flush()
  await send()
  const offered = (await input.lines()) ?? []
  for (const capability of ["clean", "smudge"])
    if (offered.includes(`capability=${capability}`)) packet(`capability=${capability}\n`)
  flush()
  await send()
  for (;;) {
    const request = await input.lines()
    if (request === undefined) return
    const command = request.find((line) => line.startsWith("command="))?.slice(8)
    const path = request.find((line) => line.startsWith("pathname="))?.slice(9) ?? "?"
    const content = await input.content()
    let result: Buffer
    try {
      result = command === "smudge" ? decrypt(key, content, path) : encrypt(key, content)
    } catch (error) {
      console.error(String(error))
      packet("status=error\n")
      flush()
      await send()
      continue
    }
    packet("status=success\n")
    flush()
    for (let at = 0; at < result.length; at += 65516) packet(result.subarray(at, at + 65516))
    flush()
    flush()
    await send()
  }
}

function git(args: string[], input?: string): string {
  const run = Bun.spawnSync(["git", ...args], { stdin: input === undefined ? "ignore" : Buffer.from(input), stderr: "inherit" })
  if (run.exitCode !== 0) throw new Error(`git ${args.join(" ")} failed`)
  return run.stdout.toString()
}

async function unlock(keyPath: string): Promise<void> {
  const key = loadKey(keyPath)
  const gitDir = resolve(git(["rev-parse", "--git-dir"]).trim())
  mkdirSync(join(gitDir, "git-crypt", "keys"), { recursive: true })
  const stored = join(gitDir, "git-crypt", "keys", "default")
  copyFileSync(keyPath, stored)
  const script = resolve(import.meta.path).replaceAll("\\", "/")
  const bun = process.execPath.replaceAll("\\", "/")
  git(["config", "filter.git-crypt.process", `"${bun}" "${script}" filter "${stored.replaceAll("\\", "/")}"`])
  git(["config", "filter.git-crypt.required", "true"])
  const files = git(["ls-files", "-z"]).split("\0").filter(Boolean)
  const attributes = git(["check-attr", "-z", "--stdin", "filter"], `${files.join("\0")}\0`).split("\0")
  const encrypted: string[] = []
  for (let i = 0; i + 2 < attributes.length; i += 3)
    if (attributes[i + 2] === "git-crypt") encrypted.push(attributes[i] as string)
  for (const file of encrypted) rmSync(file, { force: true })
  const list = join(gitDir, "git-crypt", "unlock-paths")
  writeFileSync(list, `${encrypted.join("\0")}\0`)
  git(["checkout", "--pathspec-from-file", list, "--pathspec-file-nul", "--"])
  rmSync(list)
  for (const file of encrypted)
    if (readFileSync(file).subarray(0, HEADER.length).equals(HEADER)) throw new Error(`${file} is still encrypted`)
  const dirty = git(["status", "--porcelain"]).trim()
  if (dirty !== "") throw new Error(`the checkout is not clean after unlocking:\n${dirty}`)
  console.log(`Repository unlocked: ${encrypted.length} encrypted files`)
}

if (process.argv[2] === "filter") await filter(loadKey(process.argv[3] as string))
else if (process.argv[2]) await unlock(process.argv[2])
else {
  console.error("usage: bun git-crypt-unlock.ts <key file>")
  process.exit(1)
}
