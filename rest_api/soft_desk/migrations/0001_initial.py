# Generated by Django 3.2 on 2021-05-04 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('is_active', models.BooleanField(default=True)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(blank=True, max_length=1024)),
                ('type', models.CharField(choices=[('APPL', 'Application'), ('PROD', 'Product'), ('PROJ', 'Project')], default='APPL', max_length=4)),
                ('author_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('desc', models.CharField(blank=True, max_length=2048)),
                ('tag', models.CharField(max_length=16)),
                ('priority', models.CharField(choices=[('L', 'Low'), ('N', 'Normal'), ('H', 'High'), ('U', 'Urgent'), ('I', 'Immediate')], default='N', max_length=1)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('INP', 'In Progress'), ('COM', 'Completed'), ('REJ', 'Rejected'), ('CLO', 'CLOSED')], default='NEW', max_length=3)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('assignee_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignee_user', to=settings.AUTH_USER_MODEL)),
                ('author_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_user', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soft_desk.project')),
            ],
            options={
                'unique_together': {('title', 'project', 'author_user')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=1024)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('author_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soft_desk.issue')),
            ],
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[('C', 'Create'), ('R', 'Read'), ('U', 'Update'), ('D', 'Delete')], default='R', max_length=1)),
                ('role', models.CharField(choices=[('DEV', 'Developer'), ('TES', 'Tester'), ('CRE', 'Creator'), ('ICO', 'In Charge Of')], default='CRE', max_length=3)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='soft_desk.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'project')},
            },
        ),
    ]
