from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Used when running locally only. When deploying to Google App Engine,
    # gunicorn is used as specified in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
