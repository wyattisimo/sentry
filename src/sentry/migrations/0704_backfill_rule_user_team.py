# Generated by Django 5.0.3 on 2024-04-23 14:55
import logging

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models import Q

from sentry.new_migrations.migrations import CheckedMigration
from sentry.utils.query import RangeQuerySetWrapperWithProgressBar


def backfill_rule_owners(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Rule = apps.get_model("sentry", "Rule")
    Actor = apps.get_model("sentry", "Actor")

    expr = Q(owner_user_id__isnull=True) | Q(owner_team_id__isnull=True)

    rules = Rule.objects.filter(owner_id__isnull=False).filter(expr)
    for rule in RangeQuerySetWrapperWithProgressBar(rules):
        actor = Actor.objects.get(id=rule.owner_id)
        changed = False
        if actor.user_id:
            rule.owner_user_id = actor.user_id
            changed = True
        elif actor.team_id:
            rule.owner_team_id = actor.team_id
            changed = True
        else:
            logging.info("Actor %s is neither a user or team", actor.id)
        if changed:
            rule.save(update_fields=["owner_team_id", "owner_user_id"])


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production.
    # This should only be used for operations where it's safe to run the migration after your
    # code has deployed. So this should not be used for most operations that alter the schema
    # of a table.
    # Here are some things that make sense to mark as post deployment:
    # - Large data migrations. Typically we want these to be run manually so that they can be
    #   monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   run this outside deployments so that we don't block them. Note that while adding an index
    #   is a schema change, it's completely safe to run the operation after the code has deployed.
    # Once deployed, run these manually via: https://develop.sentry.dev/database-migrations/#migration-deployment

    is_post_deployment = True

    dependencies = [
        ("sentry", "0703_add_team_user_to_rule"),
    ]

    operations = [
        migrations.RunPython(
            backfill_rule_owners,
            reverse_code=migrations.RunPython.noop,
            hints={"tables": ["sentry_rule", "sentry_actor"]},
        )
    ]
