from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('construction', '0006_laborworktype_manpowerexpense_work_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manpowerexpense',
            name='work_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='manpower_expenses', to='construction.laborworktype'),
        ),
    ] 