from invoke import task
import os


def default_env(postgres):
    os.environ['DEV_DB'] = 'True' if not postgres else 'False'
    e = os.environ
    return e


def manage(ctx, cmd, postgres=False):
    cmd = f'python manage.py {cmd}'
    ctx.run(cmd, pty=True, env=default_env(postgres))


@task
def run(ctx, ssl=False, postgres=False):
    """
    Run development server
    """
    show_dev_messages()
    if ssl:
        manage(ctx, "runsslserver 0.0.0.0:443", postgres)
    else:
        manage(ctx, "runserver 0.0.0.0:8000", postgres)

@task
def db(ctx, make=False, postgres=False):
    """
    Run migrations
    """
    if make:
        manage(ctx, "makemigrations", postgres)
        manage(ctx, "migrate", postgres)
    else:
        manage(ctx, "migrate", postgres)


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


def show_dev_messages():
    print("--------------------------------------------------------")
    print("Access ARte from external devices on the same network by accessing:")
    print("  - https://<server-device-name>")
    print("  - https://<server-device-ip>")
    print("--------------------------------------------------------")
