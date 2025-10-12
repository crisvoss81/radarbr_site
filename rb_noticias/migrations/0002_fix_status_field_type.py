# rb_noticias/migrations/0002_fix_status_field_type.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('rb_noticias', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL para PostgreSQL - converter character varying para integer
            sql="ALTER TABLE rb_noticias_noticia ALTER COLUMN status TYPE integer USING status::integer;",
            reverse_sql="ALTER TABLE rb_noticias_noticia ALTER COLUMN status TYPE character varying USING status::text;",
        ),
    ]
