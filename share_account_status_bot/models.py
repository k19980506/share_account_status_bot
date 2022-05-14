from django.db import models

# Create your models here.

class Service(models.Model):
	name = models.CharField(max_length=100)
	limit = models.IntegerField(default=1)

	# def __str__(self):
	#     return self.name

class User(models.Model):
	name = models.CharField(max_length=100)
	is_admin = models.BooleanField(default=False)
	services = models.ManyToManyField(Service, through='UserService', through_fields=('user', 'service'))

class UserService(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	service = models.ForeignKey(Service, on_delete=models.CASCADE)
	owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='owner_set')
	account = models.CharField(max_length=100)
	is_online = models.BooleanField(default=False)
	login_devices_count = models.IntegerField(default=0)
	time = models.TimeField(auto_now_add=True)
