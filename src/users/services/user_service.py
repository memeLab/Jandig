from django.contrib.auth.models import User

import logging

log = logging.getLogger("ej")


class UserService:
    def get_user_email(self, username_or_email):
        if "@" in username_or_email:
            return username_or_email
        user = User.objects.get(username=username_or_email)
        log.warning(user)
        return user.email

    def check_if_username_or_email_exist(self, username_or_email):
        if "@" in username_or_email:
            if not User.objects.filter(email=username_or_email).exists():
                return False
        else:
            if not User.objects.filter(username=username_or_email).exists():
                return False
        return True
