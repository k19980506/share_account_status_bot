from os import environ

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from share_account_status_bot.models import Service, User

import logging

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
                user = create_or_retrieve_user(event.source.user_id)
                user_id, display_name = user.user_id, user.name

                logging.debug(event.message)
                logging.debug('Text is: ' + event.message.text)
                logging.debug('Name is: ' + display_name)

                switch = {
                    'go': lambda: online(user_id),
                    'stop': lambda: offline(user_id),
                    'search': lambda: search(),
                }

                text = switch.get(event.message.text, help)()

                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=text)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def get_user_name(id):
    return line_bot_api.get_profile(id).display_name

def create_or_retrieve_user(id):
    logging.debug('UserId is: ' + id)

    try:
        user = User.objects.get(user_id=id)
    except User.DoesNotExist:
        logging.debug("start to create a new user.....")
        display_name = get_user_name(id)
        user = User(user_id=id, name=display_name)
        user.save()

    logging.debug('User ' + str(user))
    return user

def online(user):
    # user_service = UserService.objects.get(user_id=user.user_id)
    # user_service.is_online = True
    # user_service.save()
    return user.name + " online."

def offline(user):
    # user_service = UserService.objects.get(account='k19980506')
    # user_service.is_online = False
    # user_service.save()
    return user.name + " offline."

def search():
    # s = Service.objects.get(account='k19980506')
    # logging.debug('Search:' + serializers.serialize('json', [s]))
    # return "online" if s.is_online else "offline"
    return "search"

def help():
    return """
    Thanks for use this service.

    key:
        go + 'streaming service name': change your account status to online.
        stop + 'streaming service name': change your account status to offline.
        search: check the account status.

    e.g.:
        go kkbox
        stop netflix
        search
    """
