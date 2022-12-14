# Generated by Django 3.0.4 on 2022-11-08 09:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import froala_editor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('statement', froala_editor.fields.FroalaField(blank='true')),
                ('constraint', froala_editor.fields.FroalaField(blank='true')),
                ('input_format', models.TextField()),
                ('output_format', models.TextField()),
                ('sample_input', models.TextField()),
                ('sample_output', models.TextField()),
                ('explaination', models.TextField()),
                ('time_limit', models.IntegerField(default=1)),
                ('difficulty', models.CharField(max_length=10)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('due_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('branch', models.CharField(default='CS', max_length=10)),
                ('year', models.IntegerField(default=1)),
                ('input_file', models.FileField(upload_to='inputs/')),
                ('output_file', models.FileField(upload_to='outputs/')),
                ('difficultylevel', models.IntegerField(verbose_name='default=1')),
                ('auth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.TextField()),
                ('date_submitted', models.DateTimeField(default=django.utils.timezone.now)),
                ('solution_file', models.FileField(upload_to='solutions/')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
                ('usr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Problem_Feature',
            fields=[
                ('problem', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='judge.Problem')),
                ('accuracy', models.FloatField(default=0)),
                ('total_submission', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('solution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='judge.Solution')),
                ('verdict', models.TextField()),
                ('time', models.TextField()),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Problem_Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=20)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem')),
            ],
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=100)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('local_rank', models.IntegerField()),
                ('new_rating', models.IntegerField()),
                ('old_rating', models.IntegerField()),
                ('absolute', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
