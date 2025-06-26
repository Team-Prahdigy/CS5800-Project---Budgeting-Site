from flask import Flask
from flask_cors import CORS

print(">>> Flask script started")  # To confirm it's being executed

app = Flask(__name__)
CORS(app)

@app.route('/api/hello')
def hello():
    return {'message': 'Hello World'}

if __name__ == '__main__':
    print(">>> Starting Flask server")
    app.run(debug=True)
