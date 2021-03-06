#!/usr/bin/env python3

import os
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from flask import Blueprint, Flask, render_template, redirect, request, session, url_for
from blogjar.models import Models

app = Flask(__name__)
os.environ['BLOG_SETTINGS'] = './settings.cfg'
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config.from_envvar('BLOG_SETTINGS')

@app.before_request
def redirect_nonwww():
    """Redirect non-www requests to www."""
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'stephenbooher.com':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'www.stephenbooher.com'
        return redirect(urlunparse(urlparts_list), code=301)

class WebFactionMiddleware(object):
    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)

app.wsgi_app = WebFactionMiddleware(app.wsgi_app, app.config['APPLICATION_ROOT'])
models = Models(app)

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/newsroom', methods=['GET'])
def newsroom():
    if 'user_id' in session:
        return render_template('newsroom.html')
    else:
        return redirect(url_for('auth_sign_in'), 303)

@app.route('/newsroom/metrics', methods=['GET'])
def newsroom_metrics():
    if 'user_id' in session:
        return render_template('newsroom_metrics.html')
    else:
        return redirect(url_for('auth_sign_in'), 303)


@app.route('/newsroom/sign-in', methods=['GET', 'POST'])
def auth_sign_in():
    if request.method == 'GET':
        return render_template('sign_in.html')
    else:
        username = request.form['username']
        password = request.form['password']

        if not username or not password or len(password) > 160:
            return render_template('sign_in.html', error='Incorrect username or password.')

        user = models.auth(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('newsroom'), 303)
        else:
            return render_template('sign_in.html', error='Incorrect username or password.')

@app.route('/newsroom/sign-out', methods=['POST'])
def auth_sign_out():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('article_bulk'), 303)

@app.route('/authors/<author>', methods=['GET'])
def author_resource(author):
    return render_template('author.html')

# Get a list of tags
# Tags are a pseudo-resource-- it doesn't make sense to create or delete them
# directly.
@app.route('/tags', methods=['GET'])
def tag_bulk():
    return render_template('tags.html')

# View a collection of articles.
# We do not POST to /articles. Instead, we PUT to /articles/<slug>.
# TODO
@app.route('/', methods=['GET', 'POST'])
def article_bulk():
    if request.method == 'GET':
        # Filters are on the query string
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        page = request.args.get('page')
        limit = request.args.get('limit')
        query = request.args.get('query')
        tag = request.args.get('tag')
        rows = models.get_articles()
        dictrows = [dict(row) for row in rows]
        for row in dictrows:
            if 'published_date' in row:
                pubdate = datetime.strptime(row['published_date'],
                '%Y-%m-%d %H:%M:%S')
                row['published_date'] = pubdate.strftime('%b %d, %Y')
                row['copyright_years'] = pubdate.strftime('%Y')

        return render_template('articles.html', rows=dictrows)
    elif request.method == 'POST':
        if 'user_id' in session:
            return create_article()
        else:
            return render_template('403.html'), 403
    else:
        return render_template('403.html'), 405

def create_article():
    # Insert
    headline = request.form['headline']
    article = request.form['article']
    slug = request.form['slug']
    is_minor = 0
    models.create_article(headline, article, slug, is_minor, session['user_id'])
    return redirect(url_for('article_resource', slug=slug), 303)

# View, create/update, and delete a article.
@app.route('/<slug>', methods=['GET', 'PUT', 'DELETE'])
def article_resource(slug):
    if request.method == 'GET':
        article = models.get_article(slug)
        if not article:
            return render_template('404.html'), 404
        else:
            articledict = dict(article)
            pubdate = datetime.strptime(articledict['published_date'], '%Y-%m-%d %H:%M:%S')
            articledict['published_date'] = pubdate.strftime('%b %d, %Y')
            return render_template('article.html', row=articledict)
    else:
        if 'user_id' in session:
            if request.method == 'DELETE':
                models.delete_article(slug)
            elif request.method == 'PUT':
                return create_article()
            else:
                return render_template('403.html'), 405
        else:
            return render_template('403.html'), 403

# View and create comments on a article
@app.route('/<slug>/comments', methods=['GET', 'POST'])
def article_comment_bulk(slug):
    if request.method == 'GET':
        return render_template('article_comments.html')
    else:
        # Create comment from postdata
        if 'user_id' in session:
            return render_template('404.html'), 404
        else:
            return render_template('403.html'), 403

# View metrics for a article (editor-only)
@app.route('/<slug>/metrics', methods=['GET'])
def article_metrics(slug):
    if 'user_id' in session:
        return render_template('article_metrics.html')
    else:
        return render_template('403.html'), 403

# View publish history for a article (editor-only)
@app.route('/<slug>/revisions', methods=['GET'])
def article_revision_bulk(slug):
    # Philosophy: by default, keep every published revision of a article
    if 'user_id' in session:
        return render_template('article_revisions.html')
    else:
        return render_template('403.html'), 403

# View or delete a revision of a article (editor-only)
@app.route('/<slug>/revisions/<int:revision_id>', methods=['GET', 'DELETE'])
def article_revision_resource(slug, revision_id):
    # Philosophy: by default, keep every published revision of a article
    if 'user_id' in session:
        if request.method == 'GET':
            return render_template('article_revision.html')
        else:
            # TODO
            return render_template('404.html'), 404
    else:
        return render_template('403.html'), 403

# Delete or update a comment
@app.route('/<slug>/comments/<int:comment_id>', methods=['DELETE', 'PUT'])
def article_comment_resource(slug, comment_id):
    # TODO: only original commenter or editor may delete
    if 'user_id' in session:
        # TODO
        return 'TODO'
    else:
        return render_template('403.html'), 403

if __name__ == '__main__':
    app.run()
