# Generated by Django 4.0.4 on 2022-05-13 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('share_account_status_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=100)),
                ('is_online', models.BooleanField(default=False)),
                ('login_devices_count', models.IntegerField(default=0)),
                ('time', models.TimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='service',
            name='account',
        ),
        migrations.RemoveField(
            model_name='service',
            name='is_online',
        ),
        migrations.RemoveField(
            model_name='service',
            name='is_owner',
        ),
        migrations.RemoveField(
            model_name='service',
            name='time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_id',
        ),
        migrations.AddField(
            model_name='service',
            name='limit',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='user',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.RemoveField(
            model_name='user',
            name='services',
        ),
        migrations.AddField(
            model_name='user',
            name='services',
            field=models.ManyToManyField(through='share_account_status_bot.UserService', to='share_account_status_bot.service'),
        ),
        migrations.AddField(
            model_name='userservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share_account_status_bot.service'),
        ),
        migrations.AddField(
            model_name='userservice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='share_account_status_bot.user'),
        ),
    ]