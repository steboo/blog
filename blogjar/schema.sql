CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    is_author INTEGER NOT NULL,
    is_editor INTEGER NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP)
CREATE TABLE IF NOT EXISTS articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL COLLATE NOCASE,
    is_published INTEGER NOT NULL)
CREATE TABLE IF NOT EXISTS articles_revisions (
    articles_revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles (article_id),
    revision INTEGER NOT NULL,
    headline TEXT NOT NULL,
    article TEXT NOT NULL,
    published_date TEXT,
    modified_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_published INTEGER NOT NULL,
    is_minor INTEGER NOT NULL)
CREATE TABLE IF NOT EXISTS articles_revisions_authors (
    articles_revisions_author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    articles_revision_id INTEGER NOT NULL REFERENCES articles_revisions (article_revision_id),
    user_id INTEGER NOT NULL REFERENCES users (user_id))
CREATE TABLE IF NOT EXISTS articles_slugs (
    articles_slug_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles (article_id),
    slug TEXT UNIQUE NOT NULL COLLATE NOCASE,
    status INTEGER NOT NULL DEFAULT 0)
CREATE TABLE IF NOT EXISTS articles_tags (
    articles_tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles (article_id),
    tag TEXT NOT NULL COLLATE NOCASE)
CREATE INDEX IF NOT EXISTS slug_idx ON articles (slug)
CREATE INDEX IF NOT EXISTS slug_idx ON articles_slugs (slug)
CREATE INDEX IF NOT EXISTS tag_idx ON articles_tags (tag)


