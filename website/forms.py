from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(max_length=254, widget=forms.PasswordInput)


class RegistryForm(forms.Form):
    username = forms.CharField(max_length=254)
    password1 = forms.CharField(max_length=254, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=254, widget=forms.PasswordInput)
    email = forms.EmailField()

    def password_varify(self):
        """
        Check whether two passwords are the same.
        """
        if self.cleaned_data['password1'] == self.cleaned_data['password2']:
            return True
        return False


class ProjectForm(forms.Form):
    name = forms.CharField(max_length=32)
    desc = forms.CharField(max_length=256)
