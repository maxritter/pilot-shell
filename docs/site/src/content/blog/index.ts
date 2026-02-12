import { BlogArticle } from './types';

/**
 * Auto-discover blog articles from .md files with YAML frontmatter.
 * Adding a new article only requires creating the .md file — no imports to maintain.
 */
const modules = import.meta.glob('./*.md', { eager: true, query: '?raw', import: 'default' }) as Record<string, string>;

function parseFrontmatter(raw: string): { meta: Record<string, string | number | string[]>; content: string } | null {
  const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return null;

  const meta: Record<string, string | number | string[]> = {};
  for (const line of match[1].split('\n')) {
    const kv = line.match(/^(\w+):\s*(.+)$/);
    if (!kv) continue;
    const [, key, val] = kv;
    if (val.startsWith('[')) {
      meta[key] = val.slice(1, -1).split(',').map(s => s.trim().replace(/^["']|["']$/g, ''));
    } else if (/^\d+$/.test(val)) {
      meta[key] = parseInt(val, 10);
    } else {
      meta[key] = val.replace(/^["']|["']$/g, '');
    }
  }
  return { meta, content: match[2] };
}

export const articles: BlogArticle[] = Object.values(modules)
  .map((raw) => {
    const parsed = parseFrontmatter(raw as string);
    if (!parsed) return null;
    const { meta, content } = parsed;
    return {
      slug: meta.slug,
      title: meta.title,
      description: meta.description,
      date: meta.date,
      author: meta.author || 'Max Ritter',
      tags: meta.tags || [],
      readingTime: meta.readingTime || Math.ceil(content.split(/\s+/).length / 200),
      content,
      keywords: meta.keywords || '',
    } as BlogArticle;
  })
  .filter((a): a is BlogArticle => a !== null)
  .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
