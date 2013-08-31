"""
Initialize Flask app

"""
from flask import Flask, session, request

from flask_debugtoolbar import DebugToolbarExtension
from gae_mini_profiler import profiler, templatetags
from werkzeug.debug import DebuggedApplication
from flask_babel import Babel
from flask_login import LoginManager, current_user
from models import ExhibitorModel

app = Flask('application')
app.config.from_object('application.settings')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.globals['LANGUAGES'] = app.config['LANGUAGES']
app.jinja_env.globals['current_user'] = current_user

#Babel
babel = Babel(app)

@babel.localeselector
def get_locale():
    if 'locale' in session:
        return session['locale']
    return request.accept_languages.best_match(app.config['LANGUAGES'])

@babel.timezoneselector
def get_timezone():
    if 'timezone' in session:
        return session['timezone']

#login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    if userid == None:
        return None
    id = int(userid)
    member = ExhibitorModel.get_by_id(id)
    return member


@app.context_processor
def inject_profiler():
    return dict(profiler_includes=templatetags.profiler_includes())

# Pull in URL dispatch routes
import urls

# Flask-DebugToolbar (only enabled when DEBUG=True)
toolbar = DebugToolbarExtension(app)

# Werkzeug Debugger (only enabled when DEBUG=True)
if app.debug:
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

# GAE Mini Profiler (only enabled on dev server)
app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)
