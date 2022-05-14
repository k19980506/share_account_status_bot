# Generated by Django 4.0.4 on 2022-05-12 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(default='', max_length=100)),
                ('name', models.CharField(default='', max_length=100)),
                ('is_owner', models.BooleanField(default=False)),
                ('is_online', models.BooleanField(default=False)),
                ('time', models.TimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('services', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='share_account_status_bot.service')),
            ],
        ),
    ]
