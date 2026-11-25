from django.db import migrations


def link_description_placeholders(apps, schema_editor):
    """Attach the existing description placeholders to their committee.

    django CMS 5 removed the PlaceholderField. Its replacement, the
    PlaceholderRelationField, finds placeholders through the generic
    ``source`` relation of the placeholder instead of a foreign key on the
    committee, so make sure every description placeholder points to its
    committee before the foreign key is dropped.
    """
    db_alias = schema_editor.connection.alias
    Committee = apps.get_model("committees", "Committee")
    Placeholder = apps.get_model("cms", "Placeholder")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type, _ = ContentType.objects.using(db_alias).get_or_create(
        app_label="committees", model="committee"
    )
    committees = Committee.objects.using(db_alias).exclude(description__isnull=True)
    CMSPlugin = apps.get_model("cms", "CMSPlugin")
    for committee in committees:
        # Remove empty placeholders that may have been created for the
        # committee already, so there is exactly one description placeholder
        duplicates = (
            Placeholder.objects.using(db_alias)
            .filter(content_type=content_type, object_id=committee.pk, slot="description")
            .exclude(pk=committee.description_id)
        )
        for duplicate in duplicates:
            if not CMSPlugin.objects.using(db_alias).filter(placeholder=duplicate).exists():
                duplicate.delete()
        Placeholder.objects.using(db_alias).filter(pk=committee.description_id).update(
            content_type=content_type, object_id=committee.pk, slot="description"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0033_placeholder_source_data_migration"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("committees", "0007_committee_show_in_achievements"),
    ]

    operations = [
        migrations.RunPython(link_description_placeholders, migrations.RunPython.noop),
        migrations.RemoveField(model_name="committee", name="description"),
    ]
