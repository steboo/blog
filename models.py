import sqlite3
#DB_PATH = '/home/frost/webapps/sb_blog/foo.db'
DB_PATH = 'foo.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)

    #with conn:
    #c = conn.cursor()
    #
    '''INSERT INTO users (username, password, first_name, last_name, is_author, is_editor)
VALUES ('stephen', 'asdf', 'Stephen', 'Booher', 1, 1)'''
    #conn.commit()
    conn.close()

def auth(username, password):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('select user_id, username, first_name, last_name from users where username=? and password=?',
                (username, password))
        row = c.fetchone()
    conn.close()
    return row

def get_articles():
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        rows = c.execute('''select (select group_concat(u.username) from
                articles_revisions_authors ara join users u on u.user_id =
                ara.user_id where ar.articles_revision_id = ara.articles_revision_id)
                users, a.slug, max(ar.revision) as revision, ar.headline,
                ar.article, ar.published_date from
                articles_revisions ar join articles a on a.article_id = ar.article_id where
                a.is_published = 1 and ar.is_published = 1 group by ar.article_id''')
        articles = rows.fetchall()
    conn.close()
    return articles

def get_article(slug):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''select ar.article, max(ar.revision) as revision, ar.headline,
                ar.published_date from
                articles_revisions ar join articles a on a.article_id = ar.article_id where
                a.is_published = 1 and ar.is_published = 1 and a.slug = ? group by
                ar.article_id''', (slug,))
        row = c.fetchone()
    conn.close()
    return row

def create_article(headline, article, slug, is_minor, user_id):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('insert into articles (slug, is_published) values (?, ?)', (slug, 1))
        c.execute('''insert into articles_revisions (article_id, revision, headline,
                article, published_date, is_published, is_minor) values (?, ?, ?, ?,
                CURRENT_TIMESTAMP, ?, ?)''', (c.lastrowid, 1, headline, article, 1,
                    is_minor))
        c.execute('''insert into articles_revisions_authors (articles_revision_id,
        user_id) values (?, ?)''', (c.lastrowid, user_id))
        conn.commit()
    conn.close()
