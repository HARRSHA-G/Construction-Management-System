from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('construction', '0002_alter_manpowerexpense_options_alter_project_options_and_more'),
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
            options={
                'ordering': ['display_name'],
            },
        ),
        migrations.RunSQL(
            sql="""
            INSERT INTO construction_materialitem (name, display_name, is_active, created_at, updated_at)
            VALUES 
                ('brick', 'Brick', 1, NOW(), NOW()),
                ('cement', 'Cement', 1, NOW(), NOW()),
                ('steel', 'Steel', 1, NOW(), NOW()),
                ('sand', 'Sand', 1, NOW(), NOW()),
                ('aggregate', 'Jelly', 1, NOW(), NOW()),
                ('paint', 'Paint', 1, NOW(), NOW()),
                ('tiles', 'Tiles', 1, NOW(), NOW()),
                ('wood', 'Wood', 1, NOW(), NOW()),
                ('stone pebbles', 'Stone pebbles', 1, NOW(), NOW()),
                ('grinate', 'Grinate', 1, NOW(), NOW()),
                ('electrical', 'Electrical Items', 1, NOW(), NOW()),
                ('plumbing', 'Plumbing Items', 1, NOW(), NOW()),
                ('others', 'Others', 1, NOW(), NOW());
            """,
            reverse_sql="DELETE FROM construction_materialitem;"
        ),
    ] 