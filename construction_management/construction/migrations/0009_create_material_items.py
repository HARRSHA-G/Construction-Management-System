from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('construction', '0008_merge_0003_add_material_items_0007_add_work_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ] 