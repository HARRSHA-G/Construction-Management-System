from django.core.management.base import BaseCommand
from construction.models import MaterialItem

class Command(BaseCommand):
    help = 'Creates default material items'

    def handle(self, *args, **kwargs):
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
            self.stdout.write(self.style.SUCCESS(f'Successfully created material item "{name}"')) 