import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# ── 全モデルをインポート (autogenerate 用) ──────────────────────────
# auth / domain
from apps.reading.shared.domain.entities.user import User                        # noqa: F401
from apps.reading.shared.domain.entities.permission import Permission            # noqa: F401
from apps.reading.shared.domain.entities.user_permission import UserPermission   # noqa: F401
# nine star ki
from apps.reading.ninestarki.domain.entities.nine_star import NineStar           # noqa: F401
from apps.reading.ninestarki.domain.entities.star_attribute import StarAttribute # noqa: F401
# core models
from core.models.star_grid_pattern import StarGridPattern         # noqa: F401
from core.models.system_config import SystemConfig                # noqa: F401
from core.models.star_groups import StarGroups                    # noqa: F401
from core.models.recommendation_history import RecommendationHistory  # noqa: F401
from core.models.zodiac_group import ZodiacGroup                  # noqa: F401
from core.models.zodiac_group_member import ZodiacGroupMember     # noqa: F401
from core.models.solar_starts import SolarStarts                  # noqa: F401
from core.models.solar_terms import SolarTerms                    # noqa: F401
from core.models.daily_astrology import DailyAstrology            # noqa: F401
from core.models.hourly_star_zodiac import HourlyStarZodiac       # noqa: F401
from core.models.pattern_switch_date import PatternSwitchDate     # noqa: F401
from core.models.monthly_directions import MonthlyDirections      # noqa: F401
from core.models.powerstone_master import PowerStoneMaster        # noqa: F401
from core.models.admin_account_limit import AdminAccountLimit     # noqa: F401
from core.models.pdf_download_event import PdfDownloadEvent       # noqa: F401
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
