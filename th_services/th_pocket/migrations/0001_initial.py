# Generated by Django 2.1.1 on 2018-09-18 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dash_services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pocket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=255)),
                ('tag', models.CharField(blank=True, max_length=80)),
                ('url', models.URLField(max_length=255)),
                ('title', models.CharField(blank=True, max_length=80)),
                ('tweet_id', models.CharField(blank=True, max_length=80)),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dash_services.TriggerService')),
            ],
            options={
                'db_table': 'skyfolk_pocket',
            },
        ),
    ]
