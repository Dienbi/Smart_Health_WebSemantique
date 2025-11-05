# Generated manually to restore removed fields
from django.db import migrations, models
from django.utils import timezone


def set_default_values(apps, schema_editor):
    """Set default values for existing records"""
    HealthRecord = apps.get_model('health_records', 'HealthRecord')
    for record in HealthRecord.objects.all():
        if not record.health_record_name:
            record.health_record_name = f"Health Record {record.health_record_id}"
        if not record.start_date:
            record.start_date = record.date if hasattr(record, 'date') and record.date else timezone.now()
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('health_records', '0005_remove_fields_add_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthrecord',
            name='health_record_name',
            field=models.CharField(default='Health Record', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='healthrecord',
            name='start_date',
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='healthrecord',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(set_default_values, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='healthrecord',
            name='date',
        ),
    ]

