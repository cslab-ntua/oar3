# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
import click

from tabulate import tabulate
from oar.lib import config

from .. import VERSION
from .operations import sync_db, purge_db, inspect_db
from .helpers import pass_context


CONTEXT_SETTINGS = dict(auto_envvar_prefix='oar',
                        help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, chain=True)
@click.version_option(version=VERSION)
@click.option('-y', '--force-yes', is_flag=True, default=False,
              help="Never prompts for user intervention")
@click.option('--db-suffix', default="archive", help="Archive database suffix")
@click.option('--debug', is_flag=True, default=False, help="Enable Debug.")
@pass_context
def cli(ctx, force_yes, db_suffix, debug):
    """Archive OAR database."""
    ctx.force_yes = force_yes
    ctx.archive_db_suffix = db_suffix
    ctx.debug = debug
    ctx.print_db_info()
    config["LOG_FORMAT"] = '[%(levelname)s]: %(message)s'


@cli.command()
@click.option('--chunk', type=int, default=10000, help="Chunk size")
@click.option('--ignore-jobs', default=["^Terminated", "^Error"],
              multiple=True)
@pass_context
def sync(ctx, chunk, ignore_jobs):
    """ Send all resources and finished jobs to archive database."""
    ctx.chunk = chunk
    ctx.ignore_jobs = ignore_jobs
    ctx.confirm("Continue to copy old resources and jobs to the archive "
                "database?", default=True)
    sync_db(ctx)


@cli.command()
@click.option('--ignore-jobs', default=["^Terminated", "^Error"],
              multiple=True)
@click.option('--max-job-id', type=int, default=None,
              help='Purge only jobs lower than this id')
@click.option('--ignore-resources', default=["^Dead"], multiple=True)
@pass_context
def purge(ctx, ignore_resources, ignore_jobs, max_job_id):
    """ Purge old resources and old jobs from your current database."""
    ctx._cache = {}  # reset filters in case of chained commands
    ctx.ignore_resources = ignore_resources
    ctx.ignore_jobs = ignore_jobs
    ctx.max_job_id = max_job_id
    msg = "Continue to purge old resources and jobs "\
          "from your current database?"
    ctx.confirm(click.style(msg.upper(), underline=True, bold=True))
    if not purge_db(ctx):
        ctx.log("\nNothing to do.")


@cli.command()
@pass_context
def inspect(ctx):
    """ Analyze all databases."""
    rows, headers = inspect_db(ctx)
    click.echo(tabulate(rows, headers=headers))
