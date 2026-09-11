from flask import Flask, request
import os
import time
import jwt
import requests

app = Flask(__name__)

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
SERVICE_ACCOUNT = os.environ["SERVICE_ACCOUNT"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"].replace("\\n", "\n")
BOT_ID = os.environ["BOT_ID"]


def get_access_token():
    now = int(time.time())

    payload = {
        "iss": CLIENT_ID,
        "sub": SERVICE_ACCOUNT,
        "iat": now,
        "exp": now + 3600
    }

    assertion = jwt.encode(
        payload,
        PRIVATE_KEY,
        algorithm="RS256"
    )

    response = requests.post(
        "https://auth.worksmobile.com/oauth2/v2.0/token",
        data={
            "assertion": assertion,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "bot.message"
        }
    )

    print("token status:", response.status_code)
    print("token response:", response.text)

    response.raise_for_status()
    return response.json()["access_token"]


def send_message(user_id, text):
    access_token = get_access_token()

    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/users/{user_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "content": {
            "type": "text",
            "text": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("send status:", response.status_code)
    print("send response:", response.text)


@app.route("/")
def home():
    return "LINE WORKS Bot is running"


@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()

    print(data)

    if (
        data.get("type") == "message"
        and data.get("content", {}).get("type") == "text"
    ):
        user_id = data["source"]["userId"]
        message = data["content"]["text"]

        if message == "テスト":
            reply = "受信しました！Botは正常に動いています。"

        elif "有給" in message:
            reply = "有給休暇についてのご質問ですね。"

        elif "健康診断" in message:
            reply = "健康診断についてのご質問ですね。"

        elif "住所変更" in message:
            reply = "住所変更についてのご質問ですね。"

        else:
            reply = "申し訳ありません。該当する回答がありません。総務部へお問い合わせください。"

        send_message(user_id, reply)

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
