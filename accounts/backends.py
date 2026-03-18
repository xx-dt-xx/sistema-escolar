from .models import User


class IdBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(id=username)
            if user.check_password(password) and user.is_active:
                return user
        except (User.DoesNotExist, ValueError):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
