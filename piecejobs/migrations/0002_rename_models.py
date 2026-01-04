# Generated migration to rename PieceJob to BusinessService and JobApplication to ServiceApplication

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('piecejobs', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PieceJob',
            new_name='BusinessService',
        ),
        migrations.RenameModel(
            old_name='JobApplication',
            new_name='ServiceApplication',
        ),
    ]
