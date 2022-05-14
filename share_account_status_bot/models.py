from django.db import models

# Create your models here.

class Service(models.Model):
	name = models.CharField(max_length=100, unique=True)
	limit = models.IntegerField(default=1)

	def __str__(self):
	    return self.name

class User(models.Model):
	user_id = models.CharField(max_length=100)
	name = models.CharField(max_length=100)
	is_admin = models.BooleanField(default=False)
	services = models.ManyToManyField(Service, through='ServiceAccount', through_fields=('user', 'service'))

	def __str__(self):
		return self.name

class Account(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_set')
	service = models.ForeignKey(Service, on_delete=models.CASCADE)
	account = models.CharField(max_length=100)
	login_devices_count = models.IntegerField(default=0)
	users = models.ManyToManyField(User, through='AccountStatus', through_fields=('account', 'user'))

	def __str__(self):
		return self.account

class ServiceAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return "{},{},{}".format(self.user.user_id, self.service.name, self.account.account)

class AccountStatus(models.Model):
	service = models.ForeignKey(Service, on_delete=models.CASCADE)
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	is_online = models.BooleanField(default=False)
	time = models.TimeField(auto_now_add=True)

	def __str__(self):
		return "{},{},{}".format(self.user.user_id, self.service.name, self.account.account)
