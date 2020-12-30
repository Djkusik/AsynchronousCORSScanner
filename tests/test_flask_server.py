from flask import Flask
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)


@app.route("/api/v1/users")
@cross_origin(supports_credentials=True, origins=r"http://(.*)nf-ssrf.tech$")
def list_users():
    return "user example"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)