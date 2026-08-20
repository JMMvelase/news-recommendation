import { useState, useCallback } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || ''

const CATEGORY_COLORS = {
  TECH: 'var(--tag-tech)',
  POLITICS: 'var(--tag-politics)',
  BUSINESS: 'var(--tag-business)',
  SPORTS: 'var(--tag-sports)',
  ENTERTAINMENT: 'var(--tag-entertainment)',
}

function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || 'var(--tag-default)'
}

function SimilarityBar({ score }) {
  const pct = Math.round(score * 100)
  return (
    <div className="similarity">
      <div className="similarity-track">
        <div className="similarity-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="similarity-label">{pct}%</span>
    </div>
  )
}

function ArticleCard({ article, onReadMore, index }) {
  return (
    <article
      className="card"
      style={{ animationDelay: `${index * 60}ms` }}
      onClick={() => onReadMore(article)}
    >
      <div className="card-top">
        <span className="category-tag" style={{ background: getCategoryColor(article.category) }}>
          {article.category}
        </span>
        <SimilarityBar score={article.similarity} />
      </div>
      <h3 className="card-headline">{article.headline}</h3>
      <div className="card-footer">
        <a
          className="card-link"
          href={article.link}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
        >
          Read original article &rarr;
        </a>
        <span className="card-find-similar">Find similar &rarr;</span>
      </div>
    </article>
  )
}

function LoadingSkeleton() {
  return (
    <div className="results-grid">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="card skeleton" style={{ animationDelay: `${i * 80}ms` }}>
          <div className="skeleton-bar skeleton-tag" />
          <div className="skeleton-bar skeleton-title" />
          <div className="skeleton-bar skeleton-title short" />
          <div className="skeleton-bar skeleton-footer" />
        </div>
      ))}
    </div>
  )
}

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [searchCount, setSearchCount] = useState(0)

  const search = useCallback(async (q) => {
    const trimmed = q.trim()
    if (!trimmed) return

    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed, k: 8 }),
      })

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`)
      }

      const data = await res.json()
      setResults(data)
      setSearchCount((c) => c + 1)
    } catch (err) {
      setError(err.message || 'Failed to fetch recommendations')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleReadMore = useCallback((article) => {
    setHistory((prev) => [...prev])
    setQuery(article.headline)
    search(article.headline)
  }, [search])

  const handleBack = useCallback(() => {
    setHistory((prev) => prev.slice(0, -1))
    setResults(null)
    setQuery('')
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    search(query)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <h1 className="logo">NEWSMIND</h1>
            <p className="tagline">Semantic article discovery</p>
          </div>
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <h2 className="hero-title">
            Discover articles you'll want to read.
          </h2>
          <p className="hero-sub">
            Type a topic, and our embedding model finds the most semantically similar articles from a database of 209,526 news stories.
          </p>
        </section>

        <form className="search-bar" onSubmit={handleSubmit}>
          <input
            type="text"
            className="search-input"
            placeholder='Try "BlackBerry smartphone business" or "climate change policy"...'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="search-button"
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <span className="spinner" />
            ) : (
              'Recommend'
            )}
          </button>
        </form>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {loading && <LoadingSkeleton />}

        {!loading && results && (
          <>
            <div className="results-header">
              <div className="results-meta">
                {history.length > 0 && (
                  <button className="back-button" onClick={handleBack}>
                    &larr; Back
                  </button>
                )}
                <h3 className="results-title">
                  Recommendations for &ldquo;{results.query}&rdquo;
                </h3>
              </div>
              <span className="results-latency">{results.latency_ms}ms</span>
            </div>
            <div className="results-grid">
              {results.recommendations.map((article, i) => (
                <ArticleCard
                  key={`${results.query}-${i}`}
                  article={article}
                  onReadMore={handleReadMore}
                  index={i}
                />
              ))}
            </div>
          </>
        )}

        {!loading && !results && searchCount === 0 && (
          <div className="empty-state">
            <div className="empty-icon">&#9993;</div>
            <p>Enter a topic above to discover related articles</p>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Built with Sentence Transformers + FAISS &middot; 209,526 articles &middot; 384-dim embeddings</p>
      </footer>
    </div>
  )
}

export default App
