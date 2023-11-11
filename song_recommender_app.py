from flask import Flask
from logging_config import setup_logging

app = Flask(__name__)
app.logger.info('Music Recommender Flask App Started')

@app.route('/')
def hello_world():
    return '<h1>Hello, World!<h1>'

if __name__ == '__main__':
    app.run(debug=True)
