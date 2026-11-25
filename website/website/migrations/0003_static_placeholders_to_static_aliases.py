"""Move the content of the old static placeholders into static aliases.

django CMS 5 removed static placeholders (``{% static_placeholder %}``) and
its migration ``cms.0042`` drops their table. The replacement is the
``{% static_alias %}`` tag of djangocms-alias. This migration runs before the
table is dropped and turns every static placeholder into a published static
alias with the same code, moving the plugins over, so the footer content
survives the upgrade.
"""

from django.db import migrations, models

STATIC_ALIAS_CATEGORY_NAME = "Static Alias"  # djangocms_alias.constants


def static_placeholders_to_aliases(apps, schema_editor):
    db = schema_editor.connection.alias
    StaticPlaceholder = apps.get_model("cms", "StaticPlaceholder")
    Placeholder = apps.get_model("cms", "Placeholder")
    CMSPlugin = apps.get_model("cms", "CMSPlugin")
    Alias = apps.get_model("djangocms_alias", "Alias")
    AliasContent = apps.get_model("djangocms_alias", "AliasContent")
    Category = apps.get_model("djangocms_alias", "Category")
    CategoryTranslation = apps.get_model("djangocms_alias", "CategoryTranslation")
    Version = apps.get_model("djangocms_versioning", "Version")
    ContentType = apps.get_model("contenttypes", "ContentType")
    User = apps.get_model("auth", "User")

    static_placeholders = list(StaticPlaceholder.objects.using(db).all())
    if not static_placeholders:
        return

    author = (
        User.objects.using(db).filter(is_superuser=True).order_by("pk").first()
        or User.objects.using(db).order_by("pk").first()
    )
    alias_content_type, _ = ContentType.objects.using(db).get_or_create(
        app_label="djangocms_alias", model="aliascontent"
    )

    translation = (
        CategoryTranslation.objects.using(db)
        .filter(name=STATIC_ALIAS_CATEGORY_NAME)
        .first()
    )
    if translation:
        category = translation.master
    else:
        # The historical model keeps parler's save(), which does not work
        # without the translation metadata, so use the plain model save.
        category = Category()
        models.Model.save(category, using=db)
        CategoryTranslation.objects.using(db).create(
            master=category, language_code="en", name=STATIC_ALIAS_CATEGORY_NAME
        )

    for static_placeholder in static_placeholders:
        # Prefer the published content, fall back on the draft
        source = None
        for candidate_id in (static_placeholder.public_id, static_placeholder.draft_id):
            if (
                candidate_id
                and CMSPlugin.objects.using(db)
                .filter(placeholder_id=candidate_id)
                .exists()
            ):
                source = candidate_id
                break
        if source is None:
            # Empty static placeholder, the alias is created on first edit
            continue
        if author is None:
            raise RuntimeError(
                "Cannot migrate static placeholders to aliases without any user "
                "to set as the author of the published versions."
            )

        if (
            Alias.objects.using(db)
            .filter(static_code=static_placeholder.code, site__isnull=True)
            .exists()
        ):
            continue

        alias = Alias.objects.using(db).create(
            category=category,
            static_code=static_placeholder.code,
            creation_method="template",
            position=Alias.objects.using(db).filter(category=category).count(),
        )

        languages = (
            CMSPlugin.objects.using(db)
            .filter(placeholder_id=source)
            .values_list("language", flat=True)
            .distinct()
        )
        for language in sorted(set(languages)):
            content = AliasContent.objects.using(db).create(
                alias=alias, name=static_placeholder.code, language=language
            )
            # djangocms-alias names the placeholder of a static alias after
            # its static code (see AliasContent.placeholder)
            placeholder = Placeholder.objects.using(db).create(
                slot=static_placeholder.code,
                content_type=alias_content_type,
                object_id=content.pk,
            )
            CMSPlugin.objects.using(db).filter(
                placeholder_id=source, language=language
            ).update(placeholder=placeholder)
            Version.objects.using(db).create(
                content_type=alias_content_type,
                object_id=content.pk,
                created_by=author,
                number="1",
                state="published",
            )


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0002_alter_slideshow_image_description"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("cms", "0041_alter_pageurl_unique_together_pageurl_site_and_more"),
        ("djangocms_alias", "0008_alter_categorytranslation_unique_together_and_more"),
        ("djangocms_versioning", "0018_fix_typo"),
    ]

    run_before = [
        ("cms", "0042_remove_placeholderreference_placeholder_ref_and_more"),
    ]

    operations = [
        migrations.RunPython(static_placeholders_to_aliases, migrations.RunPython.noop),
    ]
