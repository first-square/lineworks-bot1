from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "LINE WORKS Bot is running"

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    print(data)

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
