import os
import sys

from invoke import task

directory = os.path.dirname(__file__)
sys.path.append("jandig")


#
# Call python manage.py in a more robust way
#
def robust_manage(ctx, cmd, env=None, **kwargs):
    kwargs = {k.replace("_", "-"): v for k, v in kwargs.items() if v is not False}
    opts = " ".join(f'--{k} {"" if v is True else v}' for k, v in kwargs.items())
    cmd = f"python3 ./src/manage.py {cmd} {opts}"
    env = {**os.environ, **(env or {})}
    path = env.get("PYTHONPATH", ":".join(sys.path))
    env.setdefault("PYTHONPATH", f"src:{path}")
    print(cmd)
    ctx.run(cmd, pty=True, env=env)


def manage(ctx, cmd):
    cmd = f"python3 ./src/manage.py {cmd}"
    ctx.run(cmd, pty=True, env=os.environ)


#
# Translations
#
@task
def i18n(ctx, edit=False, lang="pt_BR", keep_pot=False):
    """
    Extract messages for translation.
    """
    if edit:
        ctx.run(f"poedit locale/{lang}/LC_MESSAGES/django.po")
    else:
        print("Collecting messages")
        robust_manage(ctx, "makemessages", keep_pot=True, locale=lang)

        print("Extract Jinja translations")
        ctx.run("pybabel extract -F ./etc/babel.cfg -o ./locale/jinja2.pot .")

        print("Join Django + Jinja translation files")
        ctx.run(
            "msgcat ./locale/django.pot ./locale/jinja2.pot --use-first -o ./locale/join.pot",
            pty=True,
        )
        ctx.run(r"""sed -i '/"Language: \\n"/d' ./locale/join.pot""", pty=True)

        print(f"Update locale {lang} with Jinja2 messages")
        ctx.run(f"msgmerge ./locale/{lang}/LC_MESSAGES/django.po ./locale/join.pot -U")

        if not keep_pot:
            print("Cleaning up")
            ctx.run("rm ./locale/*.pot")
