from os import environ

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from share_account_status_bot.models import Service, User, Account, AccountStatus, ServiceAccount

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

                logging.debug('Text is: ' + event.message.text)

                split_text = event.message.text.split(" ")

                # try:
                action_type, params = split_text[0], split_text[1:]
                # except ValueError:
                #     line_bot_api.reply_message(
                #         event.reply_token,
                #         TextSendMessage(text='Invalid Input')
                #     )
                #     return HttpResponseBadRequest()

                switch = {
                    'go': lambda: online(user, params),
                    'stop': lambda: offline(user, params),
                    'search': lambda: search(user),
                    'add': lambda: add(user, params),
                    'use': lambda: use(user, params),
                }

                text = switch.get(action_type, help)()

                line_bot_api.reply_message(
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

    logging.debug('User: ' + str(user))
    return user

def online(user, params):
    try:
        service_name = params[0]
    except IndexError:
        return "Invalid Input"

    # user_service = UserService.objects.get(user_id=user.user_id)
    # user_service.is_online = True
    # user_service.save()
    return user.name + " online."

def offline(user, params):
    # try:
    #     service_name = params[0]
    # except IndexError:
    #     return "Invalid Input"

    # try:
    #     service = Service.objects.get(name=service_name.lower())
    # except Service.DoesNotExist:
    #     return 'Service Not Found'

    # try:
    #     service_account = ServiceAccount.objects.get(user=user, service=service)
    # except ServiceAccount.DoesNotExist:
    #     return "You don't have an account with {}\nPlease use add/use option to set account first".format(service_name)

    # user_service = UserService.objects.get(account='k19980506')
    # user_service.is_online = False
    # user_service.save()
    return user.name + " offline."

def search(user):
    # UserService.objects.filter(user_id=user.id)
    # s = Service.objects.get(account='k19980506')
    # logging.debug('Search:' + serializers.serialize('json', [s]))
    # return "online" if s.is_online else "offline"
    return "search"

def help():
    return """
    Thanks for use this service.

    key:
        go + 'service name': change your account status to online.
        stop + 'service name': change your account status to offline.
        search: check the account status.
        add + 'service name' + 'account': create your account. (If you are the account's owner)
        use + 'service name' + account: add other's account to your account list.

    e.g.:
        go kkbox
        stop netflix
        search
        add kkbox account
        use netflix account
    """

# add(user, service_name, account)
def add(user, params):
    if user.is_admin:
        try:
            [service_name, account] = params[:2]
        except IndexError:
            return "Invalid Input"

        try:
            service = Service.objects.get(name=service_name.lower())
        except Service.DoesNotExist:
            logging.debug('Start to create service ....')
            service = Service(name=service_name.lower())
            service.save()

        logging.debug('Service: ' + str(service))

        try:
            Account(owner=user, service=service, account=account)
            return "Account already created."
        except Account.DoesNotExist:
            logging.debug('Start to create account ....')
            account = Account(owner=user, service=service, account=account)
            account.save()
            logging.debug('Account: ' + str(account))

            logging.debug('Start to create service_account ....')
            service_account = ServiceAccount(user=user, service=service, account=account)
            service_account.save()
            logging.debug('ServiceAccount: ' + str(service_account))

        return "add success"
    else:
        return "Forbidden"

def use(user, params):
    try:
        [service_name, account] = params[:2]
    except IndexError:
        return "Invalid Input"

    try:
        service = Service.objects.get(name=service_name.lower())
    except Service.DoesNotExist:
        return 'Service Not Found'

    logging.debug('Service: ' + str(service))

    try:
        account = Account.objects.get(service=service, account=account)
        logging.debug('Start to create service_account ....')
        service_account = ServiceAccount(user=user, service=service, account=account)
        service_account.save()
        logging.debug('ServiceAccount: ' + str(service_account))

    except Account.DoesNotExist:
        return 'Account Not Found'

    return "use success"
