from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .fields import HoneyPotField, PasswordField, UsersEmailField, CharField, ImgField


class UserCreationForm(forms.ModelForm):

    error_messages = {
        'duplicate_email': _('该邮箱已存在'),
        'password_mismatch': _('两次输入的密码不对应'),
    }

    email = UsersEmailField(label=_('邮箱'), max_length=40)
    password1 = PasswordField(label=_('密码'))
    password2 = PasswordField(
        label=_('确认密码'),
        help_text=_('再次输入密码以进行确认'))
    profile_picture = ImgField(label=_('头像'),required=False)

    class Meta:
        model = get_user_model()
        fields = ('email',)

    def clean_email(self):

        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data['email']
        try:
            get_user_model()._default_manager.get(email=email)
        except get_user_model().DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        print('right1')
        return password2

    def save(self, commit=True):
        print('right3')
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = not settings.USERS_VERIFY_EMAIL
        if commit:
            print('right2')
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(label=_('Password'), help_text=_(
        '为安全着想原密码未储存， '
        '这是储存的哈希密码，但你能使用'
        '<a href=\"password/\">这个页面</a>来修改密码。'))

    class Meta:
        model = get_user_model()
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial['password']


class RegistrationForm(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    tos = forms.BooleanField(
        label=_('I have read and agree to the Terms of Service'),
        widget=forms.CheckboxInput,
        error_messages={
            'required': _('You must agree to the terms to register')
        })


class RegistrationFormHoneypot(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a honeypot field
    for Spam Prevention

    """
    accept_terms = HoneyPotField()


class UserActiveForm(forms.ModelForm):
    code = CharField(label=_('验证码'), help_text=_('保存后自动生成验证码'))
