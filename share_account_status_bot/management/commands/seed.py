import logging
from django.core.management.base import BaseCommand

from share_account_status_bot.models import Service, User, Account, AccountStatus

""" Clear all data and creates dummy data """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'

class Command(BaseCommand):
	help = "seed database for testing and development."

	def add_arguments(self, parser):
		parser.add_argument('--mode', type=str, help="Mode")

	def handle(self, *args, **options):
		self.stdout.write('seeding data...')
		run_seed(self, options['mode'])
		self.stdout.write('done.')

def clear_data():
	"""Deletes all the table data"""
	logging.info("Delete instances")
	User.objects.all().delete()
	Service.objects.all().delete()
	Account.objects.all().delete()
	AccountStatus.objects.all().delete()

def create_data():
	logging.info("Creating data")

	service = Service(name='kkbox')
	service.save()
	logging.info("{} service created.".format(service))
	user = User(user_id='U8a2912a17e66769d21cae5d95c628d5f', name='尚軒·ࡇ·', is_admin=True)
	user.save()
	logging.info("{} user created.".format(user))
	account = Account(owner=user, service=service, account='k19980506')
	account.save()
	logging.info("{} account created.".format(account))
	account_status = AccountStatus(service=service, account=account, user=user)
	account_status.save()
	logging.info("account_status created.")

	return user

def run_seed(self, mode):
	""" Seed database based on mode

	:param mode: refresh / clear
	:return:
	"""
	# Clear data from tables
	clear_data()
	if mode == MODE_CLEAR:
		return

	# Creating dara
	create_data()
