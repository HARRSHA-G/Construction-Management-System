from django.db import migrations

def create_default_material_items(apps, schema_editor):
    MaterialItem = apps.get_model('construction', 'MaterialItem')
    default_items = [
        ('brick', 'Brick'),
        ('cement', 'Cement'),
        ('steel', 'Steel'),
        ('sand', 'Sand'),
        ('aggregate', 'Jelly'),
        ('paint', 'Paint'),
        ('tiles', 'Tiles'),
        ('wood', 'Wood'),
        ('stone pebbles', 'Stone pebbles'),
        ('grinate', 'Grinate'),
        ('electrical', 'Electrical Items'),
        ('plumbing', 'Plumbing Items'),
        ('others', 'Others')
    ]
    
    for code, name in default_items:
        MaterialItem.objects.get_or_create(
            name=code,
            defaults={'display_name': name}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('construction', '0002_alter_manpowerexpense_options_alter_project_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_material_items),
    ] 