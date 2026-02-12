import { useState, useMemo, useEffect } from 'react';
import { Link } from 'react-router-dom';
import NavBar from '@/components/NavBar';
import Footer from '@/components/Footer';
import SEO from '@/components/SEO';
import { articles } from '@/content/blog';
import { Search, Clock, BookOpen } from 'lucide-react';

const ROTATING_WORDS = ['Guides', 'Tutorials', 'Insights', 'Tips', 'Workflows'];

const BlogPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [rotatingIndex, setRotatingIndex] = useState(0);

  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    const interval = setInterval(() => {
      setRotatingIndex((prev) => (prev + 1) % ROTATING_WORDS.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const allTags = useMemo(() => {
    const tagSet = new Set<string>();
    articles.forEach((a) => a.tags.forEach((t) => tagSet.add(t)));
    return Array.from(tagSet).sort();
  }, []);

  const filteredArticles = useMemo(() => {
    let result = [...articles];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (a) =>
          a.title.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q) ||
          a.tags.some((t) => t.toLowerCase().includes(q))
      );
    }

    if (activeTag) {
      result = result.filter((a) => a.tags.includes(activeTag));
    }

    result.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

    return result;
  }, [searchQuery, activeTag]);

  const blogStructuredData = {
    "@context": "https://schema.org",
    "@type": "Blog",
    "name": "Claude Pilot Blog",
    "description": "Guides and insights on Claude Code, AI-powered development workflows, TDD enforcement, and quality automation",
    "url": "https://claude-pilot.com/blog",
    "publisher": {
      "@type": "Organization",
      "name": "Claude Pilot",
      "url": "https://claude-pilot.com"
    }
  };

  return (
    <>
      <SEO
        title="Blog - Claude Pilot"
        description="Learn how to master Claude Code with our in-depth guides on TDD enforcement, context management, and custom rules configuration."
        keywords="Claude Code blog, AI development guides, TDD enforcement, Claude Code tutorials, context management, custom rules"
        canonicalUrl="https://claude-pilot.com/blog"
        structuredData={blogStructuredData}
      />
      <NavBar />
      <main className="min-h-screen bg-background pt-24">
        <div className="container mx-auto px-4 py-16">
          {/* Hero Section */}
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
              <span>Claude Pilot </span>
              <span className="relative inline-block">
                <span
                  key={rotatingIndex}
                  className="inline-block bg-primary/20 text-primary px-4 py-1 rounded-lg animate-fade-in-up"
                >
                  {ROTATING_WORDS[rotatingIndex]}
                </span>
              </span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Master Claude Code — guides, workflows, and best practices
            </p>
          </div>

          {/* Search & Filters — single row */}
          <div className="max-w-5xl mx-auto mb-8">
            <div className="flex items-center gap-3 flex-wrap">
              {/* Search Bar */}
              <div className="relative w-56">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-sm bg-card border border-border rounded-full text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/25 transition-colors"
                />
              </div>

              {/* Category Tags */}
              <button
                onClick={() => setActiveTag(null)}
                className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                  activeTag === null
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-card text-muted-foreground border-border hover:border-primary/50'
                }`}
              >
                All
              </button>
              {allTags.slice(0, 4).map((tag) => (
                <button
                  key={tag}
                  onClick={() => setActiveTag(activeTag === tag ? null : tag)}
                  className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                    activeTag === tag
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-card text-muted-foreground border-border hover:border-primary/50'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* Articles Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {filteredArticles.map((article) => (
              <Link
                key={article.slug}
                to={`/blog/${article.slug}`}
                className="group"
              >
                <article className="h-full bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
                  {/* Title with Icon */}
                  <div className="flex items-start gap-3 mb-3">
                    <BookOpen className="w-5 h-5 text-primary shrink-0 mt-1" />
                    <h2 className="text-lg font-bold group-hover:text-primary transition-colors">
                      {article.title}
                    </h2>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
                    {article.description}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {article.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Footer: Reading time & Date */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground pt-3 border-t border-border">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{article.readingTime} min read</span>
                    </div>
                    <time dateTime={article.date}>
                      {new Date(article.date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </time>
                  </div>
                </article>
              </Link>
            ))}
          </div>

          {/* Empty State */}
          {filteredArticles.length === 0 && (
            <div className="text-center text-muted-foreground py-12 max-w-5xl mx-auto">
              <p>No articles match your search. Try a different query or category.</p>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
};

export default BlogPage;
