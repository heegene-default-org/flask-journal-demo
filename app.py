from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_babel import Babel, _, get_locale, ngettext
import os
from datetime import datetime, timezone
import json
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-dev-secret-key-change-in-production')

# Configuration for Babel
app.config['LANGUAGES'] = {
    'ko': '한국어',
    'en': 'English'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'ko'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

babel = Babel()

# Simple in-memory storage for journal entries
journal_entries = []

def locale_selector():
    # 1. Check if user has explicitly set a language
    if 'language' in session:
        return session['language']
    
    # 2. Check browser's preferred language
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or app.config['BABEL_DEFAULT_LOCALE']

babel.init_app(app, locale_selector=locale_selector)

# Make get_locale available in templates
app.jinja_env.globals.update(get_locale=get_locale)

@app.route('/')
def index():
    return render_template('index.html', entries=journal_entries)

@app.route('/new', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if title and content:
            entry = {
                'id': str(uuid.uuid4()),  # Use UUID for unique IDs
                'title': title,
                'content': content,
                'date': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            journal_entries.append(entry)
            flash(_('Journal entry created successfully!'), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('Please fill in both title and content.'), 'error')
    
    return render_template('new_entry.html')

@app.route('/edit/<entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = next((e for e in journal_entries if e['id'] == entry_id), None)
    
    if not entry:
        flash(_('Journal entry not found.'), 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if title and content:
            entry['title'] = title
            entry['content'] = content
            flash(_('Journal entry updated successfully!'), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('Please fill in both title and content.'), 'error')
    
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete/<entry_id>')
def delete_entry(entry_id):
    global journal_entries
    journal_entries = [e for e in journal_entries if e['id'] != entry_id]
    flash(_('Journal entry deleted successfully!'), 'success')
    return redirect(url_for('index'))

@app.route('/set_language/<language>')
def set_language(language=None):
    # Validate language to prevent malicious input
    if language in app.config['LANGUAGES']:
        session['language'] = language
    
    # Only redirect to safe, known routes to prevent open redirect
    safe_referrer = None
    if request.referrer:
        try:
            from urllib.parse import urlparse
            parsed_referrer = urlparse(request.referrer)
            parsed_host = urlparse(request.host_url)
            
            # Check if referrer is from same host and has safe path
            if (parsed_referrer.netloc == parsed_host.netloc and 
                parsed_referrer.path in ['/', '/new', '/edit'] or 
                parsed_referrer.path.startswith('/edit/')):
                safe_referrer = request.referrer
        except:
            # If any parsing fails, use default redirect
            pass
    
    return redirect(safe_referrer or url_for('index'))

if __name__ == '__main__':
    # Use debug mode only in development environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)