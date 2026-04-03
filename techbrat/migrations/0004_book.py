from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('techbrat', '0003_delete_userexperience'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=100)),
                ('domain', models.CharField(max_length=100)),
                ('level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20)),
                ('book_type', models.CharField(choices=[('theory', 'Theory'), ('practical', 'Practical'), ('interview', 'Interview Prep')], default='theory', max_length=20)),
                ('description', models.TextField()),
                ('link', models.URLField()),
                ('is_ai_generated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['level'], name='techbrat_bo_level_2c0f49_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['domain'], name='techbrat_bo_domain_4707e6_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['book_type'], name='techbrat_bo_book_ty_02f762_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['is_ai_generated'], name='techbrat_bo_is_ai_g_f68d9a_idx'),
        ),
    ]
