from flask import Blueprint, render_template

app = Blueprint('frontend', __name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/interactive', methods=['GET'])
def interactive():
    return render_template('interactive.html')

if __name__ == '__main__':
    app.run(debug=True)
