from users.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["userid", "nickname", "password1", "password2", "email"]


class UserUpdateForm(UserChangeForm):

    class Meta:
        model = User
        fields = ["nickname", "email"]


