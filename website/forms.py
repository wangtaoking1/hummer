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


class SourceForm(forms.Form):
    name = forms.CharField(max_length=32)
    version = forms.CharField(max_length=32)
    desc = forms.CharField(max_length=256)
    build_type = forms.IntegerField()
    image_type = forms.IntegerField()
    dockerfile = forms.CharField(max_length=256)

class ImageForm(forms.Form):
    name = forms.CharField(max_length=32)
    version = forms.CharField(max_length=32)
    desc = forms.CharField(max_length=256)
    build_type = forms.CharField()
    image_type = forms.CharField()
    old_name = forms.CharField(max_length=32)
    old_version = forms.CharField(max_length=32)

class SnapshotForm(forms.Form):
    name = forms.CharField(max_length=32)
    version = forms.CharField(max_length=32)
    desc = forms.CharField(max_length=256)
    build_type = forms.IntegerField()
    image_type = forms.IntegerField()

class ApplicationForm(forms.Form):
    image = forms.IntegerField()
    name = forms.CharField(max_length=32)
    replicas = forms.IntegerField()
    resource_limit = forms.IntegerField()
    service_type = forms.CharField()
    session_affinity = forms.CharField()
    env_number = forms.IntegerField()
    port_number = forms.IntegerField()
    volume_number = forms.IntegerField()


class VolumeForm(forms.Form):
    name = forms.CharField(max_length=32)
    desc = forms.CharField(max_length=256)
    capacity = forms.IntegerField()
    capacity_unit = forms.CharField()
