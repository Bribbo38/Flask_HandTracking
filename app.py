from flask import Flask, url_for, render_template

from blueprints.frontend import app as front_app
from blueprints.backend import app as back_app

app = Flask(__name__)

app.register_blueprint(front_app, url_prefix='/')
app.register_blueprint(back_app, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
