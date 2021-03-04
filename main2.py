# -*- coding: utf-8 -*-
from flask import Flask, request, abort, send_file

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, LocationMessage, LocationSendMessage,TextSendMessage, StickerSendMessage, MessageImagemapAction, ImagemapArea, ImagemapSendMessage, BaseSize,CarouselTemplate, CarouselColumn,URITemplateAction
)
from linebot.exceptions import LineBotApiError

import pandas as pd
#import scrape as sc
import urllib3.request
import os
import sys
from io import BytesIO, StringIO
import requests

app = Flask(__name__)

#YOUR_CHANNEL_ACCESS_TOKEN = os.environ["qUtZDwJ7fVL+O2sjfhCgNVwG6ys61WIhQZo6n+qR+GXMKEDDlBk13HAfP3+1rOl0a8khgN46FAiCqaMGRWfwaFfBvVydMTEqEkkYTJuAvsG+F8/Gz8JT9LMGKbIPvPczSKVDjLqsxp2kHF+SLypLQgdB04t89/1O/w1cDnyilFU="]
#YOUR_CHANNEL_SECRET = os.environ["d13804e2693f248b9bfecb93b5c029ef"]

line_bot_api = LineBotApi('07mVvdyHI9oYQ3XENW3uBPwznaQVVHE1iMIcTA5p31bPBB1snc1Oz1AHRlWbY0l8a8khgN46FAiCqaMGRWfwaFfBvVydMTEqEkkYTJuAvsF3HgATVg1n6sUmB7mXB1PAj6SXlWbB/q686gU+WPWZ5QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('36f979209515fe6735d3885e21db505a')

line_user_id = "Uda02fd3377939c200ac4cf59e7a04bd8"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # LINE DevelopersからこのreplyTokenが来たときにエラーになるのを回避
    if event.reply_token == "00000000000000000000000000000000":
        return
    
    text = event.message.text
    if '' in event.message.text:
        line_bot_api.reply_message(
        event.reply_token,
        [
        TextSendMessage(text='位置情報を教えてください。'),
        TextSendMessage(text='line://nv/location')
        ]
        )

# csvファイル読み込み
df = pd.read_csv("location_data.csv")
    
@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    addr = str(event.message.address)
    miss = 0
    for index, row in df.iterrows():
        if df.at[index,'k'] in addr:
            message = "\n{}\n「{}」\n{}\n".format(
                "最適な休憩場所は",
                df.at[index,'n'],
                "です。"+chr(0x100001)
            )

            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=message),
                      LocationSendMessage(
                          title=df.at[index,'n'],
                          address=df.at[index,'address'],
                          latitude=df.at[index,'latitude'],
                          longitude=df.at[index,'longitude']
                     )
                ]
             )
        else:
            miss += 1
        
        
    if miss == 60:
        line_bot_api.reply_message(
        event.reply_token,
        [
        TextSendMessage(text='すみません。この地域には対応していません。'),
        ]
        )

    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)