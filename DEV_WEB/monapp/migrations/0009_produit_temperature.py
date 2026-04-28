from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monapp', '0008_personne_email_confirme_personne_token_confirmation'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='temperature',
            field=models.FloatField(default=22.0),
        ),
    ]
