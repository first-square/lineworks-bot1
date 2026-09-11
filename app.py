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


def send_button_menu(user_id, title, buttons):
    access_token = get_access_token()

    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/users/{user_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    actions = []

    for button in buttons:
        actions.append({
            "type": "message",
            "label": button,
            "text": button
        })

    data = {
        "content": {
            "type": "button_template",
            "contentText": title,
            "actions": actions
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("menu status:", response.status_code)
    print("menu response:", response.text)


def send_main_menu(user_id):
    send_button_menu(
        user_id,
        "お問い合わせ内容を選択してください。",
        [
            "勤怠",
            "給与",
            "備品発注",
            "企業型確定拠出年金",
            "各種届出",
            "通勤関連",
            "金銭関連",
            "給与システム",
            "korette",
            "店舗設備"
        ]
    )


def send_salary_menu(user_id):
    send_button_menu(
        user_id,
        "給与に関する内容を選択してください。",
        [
            "通勤費・交通費",
            "各種手当",
            "賞与"
        ]
    )


def send_supplies_menu(user_id):
    send_button_menu(
        user_id,
        "備品発注に関する内容を選択してください。",
        [
            "たのめーる",
            "収入印紙"
        ]
    )


def send_notification_menu(user_id):
    send_button_menu(
        user_id,
        "各種届出に関する内容を選択してください。",
        [
            "住所変更",
            "家族異動",
            "扶養加入・削除",
            "休職・産休・育児休業",
            "退職"
        ]
    )


def send_commute_menu(user_id):
    send_button_menu(
        user_id,
        "通勤関連の内容を選択してください。",
        [
            "マイカー通勤申請",
            "通勤経路",
            "通勤費・交通費"
        ]
    )


def send_money_menu(user_id):
    send_button_menu(
        user_id,
        "金銭関連の内容を選択してください。",
        [
            "レジ清算・返品処理",
            "支払準備金",
            "クレジット関連",
            "月末残高報告書",
            "入金",
            "PayPay関連"
        ]
    )


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

        # 最初のメニュー
        if message in ["メニュー", "問い合わせ", "開始"]:
            send_main_menu(user_id)

        # 1階層目
        elif message == "勤怠":
            send_message(
                user_id,
                "「勤怠」に関するお問い合わせは、総務部までお願いいたします。"
            )

        elif message == "給与":
            send_salary_menu(user_id)

        elif message == "備品発注":
            send_supplies_menu(user_id)

        elif message == "企業型確定拠出年金":
            send_message(
                user_id,
                "「企業型確定拠出年金」に関するお問い合わせは、総務部までお願いいたします。"
            )

        elif message == "各種届出":
            send_notification_menu(user_id)

        elif message == "通勤関連":
            send_commute_menu(user_id)

        elif message == "金銭関連":
            send_money_menu(user_id)

        elif message == "給与システム":
            send_message(
                user_id,
                "「給与システム」に関するお問い合わせは、総務部までお願いいたします。"
            )

        elif message == "korette":
            send_message(
                user_id,
                "「korette」に関するお問い合わせは、営業戦略部までお願いいたします。"
            )

        elif message == "店舗設備":
            send_message(
                user_id,
                "「店舗設備」に関するお問い合わせは、営業戦略部までお願いいたします。"
            )

        # 給与
        elif message == "通勤費・交通費":
            send_message(
                user_id,
                "「通勤費・交通費」に関するお問い合わせは、経理課までお願いいたします。"
            )

        elif message == "各種手当":
            send_message(
                user_id,
                "「各種手当」に関するお問い合わせは、各エリア長までお願いいたします。"
            )

        elif message == "賞与":
            send_message(
                user_id,
                "「賞与」に関するお問い合わせは、各エリア長までお願いいたします。"
            )

        # 備品発注
        elif message == "たのめーる":
            send_message(
                user_id,
                "「たのめーる」に関するお問い合わせは、総務部までお願いいたします。"
            )

        elif message == "収入印紙":
            send_message(
                user_id,
                "「収入印紙」に関するお問い合わせは、総務部までお願いいたします。"
            )

        # 各種届出
        elif message in [
            "住所変更",
            "家族異動",
            "扶養加入・削除",
            "休職・産休・育児休業",
            "退職"
        ]:
            send_message(
                user_id,
                f"「{message}」に関するお問い合わせは、総務部までお願いいたします。"
            )

        # 通勤関連
        elif message == "マイカー通勤申請":
            send_message(
                user_id,
                "「マイカー通勤申請（開始・取りやめ）」に関するお問い合わせは、総務部までお願いいたします。"
            )

        elif message == "通勤経路":
            send_message(
                user_id,
                "「通勤経路」に関するお問い合わせは、経理課までお願いいたします。"
            )

        # 金銭関連
        elif message in [
            "レジ清算・返品処理",
            "支払準備金",
            "クレジット関連",
            "月末残高報告書",
            "入金",
            "PayPay関連"
        ]:
            send_message(
                user_id,
                f"「{message}」に関するお問い合わせは、経理課までお願いいたします。"
            )

        else:
            send_message(
                user_id,
                "「メニュー」と入力すると、お問い合わせ項目を選択できます。"
            )

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
