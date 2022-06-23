from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from .models import CustomUser

class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'location', 'about', 'phone_number', 'account_type']

class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'location', 'about', 'phone_number', 'account_type']

class CustomUserChangePasswordForm(SetPasswordForm):
    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']

class CustomUserDisplayPhotoForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['display_photo',]
