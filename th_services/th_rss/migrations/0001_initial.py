# Generated by Django 2.1.1 on 2018-09-18 18:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dash_services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=255)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('url', models.URLField(max_length=255)),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dash_services.TriggerService')),
            ],
            options={
                'db_table': 'skyfolk_rss',
            },
        ),
    ]
