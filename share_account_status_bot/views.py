from os import environ

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from share_account_status_bot.models import Service, User, Account, AccountStatus

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
                action_type, params = split_text[0], split_text[1:]

                switch = {
                    'go': lambda: online(user, params),
                    'stop': lambda: offline(user, params),
                    'search': lambda: search(user, params),
                    'add': lambda: add(user, params),
                    'use': lambda: use(user, params),
                }

                text = switch.get(action_type.lower(), help)()

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
        service_name = service_name.lower()
    except IndexError:
        return "Invalid Input"

    try:
        service = Service.objects.get(name=service_name)
    except Service.DoesNotExist:
        return 'Service Not Found'

    try:
        account_status = AccountStatus.objects.get(service=service, user=user)
        account_status.is_online = True
        account_status.save()
    except AccountStatus.DoesNotExist:
        return "You don't have an account with {}\nPlease use add/use option to set account first".format(service_name)

    logging.debug('Service {}, online'.format(service.name))
    return 'Hi {}, {} successfully launched.'.format(user.name, service_name)

def offline(user, params):
    try:
        service_name = params[0]
        service_name = service_name.lower()
    except IndexError:
        return "Invalid Input"

    try:
        service = Service.objects.get(name=service_name)
    except Service.DoesNotExist:
        return 'Service Not Found'

    try:
        account_status = AccountStatus.objects.get(service=service, user=user)
        account_status.is_online = False
        account_status.save()
    except AccountStatus.DoesNotExist:
        return "You don't have an account with {}\nPlease use add/use option to set account first".format(service_name)

    logging.debug('Service {}, offline'.format(service.name))
    return 'Hi {}, {} was successfully offline.'.format(user.name, service_name)

def check_account_status(account_status):
    same_account_users = list(account_status.account.accountstatus_set.all())
    using_users = [same_account_users[i] for i in range(len(same_account_users)) if same_account_users[i].is_online]

    if len(using_users):
        users = ','.join(i.user.name for i in using_users)
        return "{} account: {}, {} in use.".format(account_status.service.name, account_status.account.account, users)
    else:
        return "{} account: {} not in use.".format(account_status.service.name, account_status.account.account)

def search(user, params):
    logging.debug("Before search: {}".format(params))
    try:
        service_name = params[0]
        service_name = service_name.lower()

        try:
            service = Service.objects.get(name=service_name)
        except Service.DoesNotExist:
            return 'Service Not Found'

        accounts = user.accountstatus_set.filter(service=service)
    except IndexError:
        accounts = user.accountstatus_set.all()

    if len(accounts):
        return "\n".join(list(map(check_account_status, accounts)))
    else:
        return "You don't have any account.\nPlease use add/use option to set account first"


def help():
    return """
    Thanks for using this service.
    Please use 'search' to check account status before you use 'go'.

    key:
        [at first]
        add + 'service name' + 'account': create your account. (If you are the account's owner)
        use + 'service name' + account: add other's account to your account list.
        -------
        search + 'service name': check the account status. (service name is optional, if you want to check all services, you can just input 'search')
        go + 'service name': change your account status to online.
        stop + 'service name': change your account status to offline.

    e.g.:
        add kkbox account
        use netflix account
        search
        search kkbox
        go kkbox
        stop netflix
    """

# add(user, service_name, account)
def add(user, params):
    logging.debug("Before add: {}".format(params))
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
        Account.objects.get(owner=user, service=service, account=account)
        return "Account already created."
    except Account.DoesNotExist:
        logging.debug('Start to create account ....')
        account = Account(owner=user, service=service, account=account)
        account.save()
        logging.debug('Account: ' + str(account))
        logging.debug('Start to create account_status ....')
        account_status = AccountStatus(service=service, account=account, user=user)
        account_status.save()
        logging.debug('AccountStatus: ' + str(account_status))

    return "add success"

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
        logging.debug('Start to create account_status ....')
        account_status = AccountStatus(service=service, account=account, user=user)
        account_status.save()
        logging.debug('AccountStatus: ' + str(account_status))

    except Account.DoesNotExist:
        return 'Account Not Found'

    return "use success"
