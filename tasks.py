from invoke import task
import os
import subprocess


def default_env(postgres, whitenoise):
    os.environ['DEV_DB'] = 'True' if not postgres else 'False'
    os.environ['DEV_STATIC'] = 'True' if whitenoise else 'Falsse'
    e = os.environ
    return e


def manage(ctx, cmd, postgres=False, whitenoise=False):
    cmd = f'python ARte/manage.py {cmd}'
    ctx.run(cmd, pty=True, env=default_env(postgres, whitenoise))


@task
def run(ctx, ssl=False, gunicorn=False, postgres=False, whitenoise=False):
    """
    Run development server
    """
    if gunicorn:
        ctx.run('gunicorn --bind 0.0.0.0:8000 config.wsgi')
    else:
        manage(ctx, "runserver 0.0.0.0:8000", postgres, whitenoise)
    


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
    manage(ctx, "collectstatic --no-input --clear")


@task
def install_deps(ctx):
    """
    Install all dependencies
    """
    ctx.run('pip install -r etc/requirements.txt')


@task
def docker(ctx, build=False):
    command = 'sudo docker-compose -f docker/docker-compose.yml up'

    if build:
        command += ' --build'

    ctx.run(command)


@task
def build_base(ctx, publish=False):
    """
    Build base docker images
    """
    command = './etc/scripts/build-base.sh'
    
    if publish:
        command += ' publish'   
    
    ctx.run(command)


@task
def init_production(ctx):
    """
    Init production environment
    """
    command = './etc/scripts/init-production.sh'
    ctx.run(command)
