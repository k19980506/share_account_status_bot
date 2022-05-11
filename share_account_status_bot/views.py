from os import environ
from sysconfig import get_scheme_names

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

import logging
import requests
import json

# Create your views here.

logging.basicConfig(level=logging.DEBUG)

LINE_CHANNEL_ACCESS_TOKEN = environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_CHANNEL_SECRET = environ['LINE_CHANNEL_SECRET']

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
  if request.method == 'POST':
      signature = request.META['HTTP_X_LINE_SIGNATURE']
      body = request.body.decode('utf-8')

      try:
          events = parser.parse(body, signature)  # 傳入的事件
      except InvalidSignatureError:
          return HttpResponseForbidden()
      except LineBotApiError:
          return HttpResponseBadRequest()

      for event in events:
          if isinstance(event, MessageEvent):  # 如果有訊息事件
              display_name = get_user_name(event.source.user_id)

              logging.debug('UserId is: ' + event.source.user_id)
              logging.debug('Text is: ' + event.message.text)
              logging.debug('Name is: ' + display_name)

              text = 'Hi ' + display_name + "\n" + event.message.text
              line_bot_api.reply_message(  # 回復傳入的訊息文字
                  event.reply_token,
                  TextSendMessage(text=text)
              )
      return HttpResponse()
  else:
      return HttpResponseBadRequest()

def get_user_name(user_id):
    header = {'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN}
    response = requests.get('https://api.line.me/v2/bot/profile/' + user_id, headers = header)

    logging.debug("User Profile: " + str(response.json()))

    return response.json()['displayName']
