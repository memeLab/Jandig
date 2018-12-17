from invoke import task
import os


def default_env():
    os.environ['DEV_DB'] = 'true'
    e = os.environ

    return e


def manage(ctx, cmd):
    cmd = f'sudo -E python ARte/manage.py {cmd}'
    ctx.run(cmd, pty=True, env=default_env())


@task
def run(ctx):
    """
    Run development server
    """
    manage(ctx, "runsslserver 0.0.0.0:443")


@task
def db(ctx, make=False):
    """
    Run migrations
    """
    if make:
        manage(ctx, "makemigrations")
        manage(ctx, "migrate")
    else:
        manage(ctx, "migrate")


@task
def collect(ctx):
    """
    Collect static files
    """
    manage(ctx, "collectstatic --no-input")


@task
def install_deps(ctx):
    """
    Install all dependencies
    """
    ctx.run('pip install -r etc/requirements.txt')
