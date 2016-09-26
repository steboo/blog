import sqlite3
import markdown2

class Models(object):
    def __init__(self, app):
        self.app = app

    def _dict_from_row(self, row):
        return dict(zip(row.keys(), row))

    def init_db(self):
        conn = sqlite3.connect(self.app.config['DATABASE_URI'])

        #with conn:
        #c = conn.cursor()
        #
        '''INSERT INTO users (username, password, first_name, last_name, is_author, is_editor)
    VALUES ('stephen', 'asdf', 'Stephen', 'Booher', 1, 1)'''
        #conn.commit()
        conn.close()

    def auth(self, username, password):
        conn = sqlite3.connect(self.app.config['DATABASE_URI'])
        with conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('select user_id, username, first_name, last_name from users where username=? and password=?',
                    (username, password))
            row = c.fetchone()
        conn.close()
        return row

    def get_articles(self):
        conn = sqlite3.connect(self.app.config['DATABASE_URI'])
        with conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            rows = c.execute('''select (select group_concat(u.username) from
                    articles_revisions_authors ara join users u on u.user_id =
                    ara.user_id where ar.articles_revision_id = ara.articles_revision_id)
                    users, a.slug as slug, max(ar.revision) as revision, ar.headline as headline,
                    ar.article as article, ar.published_date as published_date from
                    articles_revisions ar join articles a on a.article_id = ar.article_id where
                    a.is_published = 1 and ar.is_published = 1 group by
                    ar.article_id order by published_date desc''')
            articles = rows.fetchall()
        conn.close()
        articles = [self._dict_from_row(article) for article in articles]
        for article in articles:
            # TODO: cache. will something like memcached work for articles?
            # cassandra? redis? cache in pgsql?
            article['article'] = markdown2.markdown(article['article'])

        return articles

    def get_article(self, slug):
        conn = sqlite3.connect(self.app.config['DATABASE_URI'])
        with conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('''select ar.article as article, max(ar.revision) as revision, ar.headline as headline,
                    ar.published_date as published_date from
                    articles_revisions ar join articles a on a.article_id = ar.article_id where
                    a.is_published = 1 and ar.is_published = 1 and a.slug = ? group by
                    ar.article_id''', (slug,))
            row = c.fetchone()
        conn.close()
        article = self._dict_from_row(row)
        # TODO: cache. will something like memcached work for articles?
        # cassandra? redis? cache in pgsql?
        article['article'] = markdown2.markdown(article['article'])
        return article

    def create_article(self, headline, article, slug, is_minor, user_id):
        conn = sqlite3.connect(self.app.config['DATABASE_URI'])
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
