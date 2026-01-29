from django import forms
from .models import User, Institution

class CustomSignupForm(forms.ModelForm):
    institute = forms.ModelChoiceField(
        queryset=Institution.objects.all(),
        required=False,
        to_field_name='id'
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'middle_initial',
            'last_name',
            'nationality',
            'job_title',
            'institute',
            'department',
            'disability',
            'dietary',
        ]

    def signup(self, request, user):
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.middle_initial = self.cleaned_data['middle_initial']
        user.last_name = self.cleaned_data['last_name']
        user.nationality = self.cleaned_data['nationality']
        user.job_title = self.cleaned_data['job_title']
        user.institute = self.cleaned_data['institute']
        user.department = self.cleaned_data['department']
        user.disability = self.cleaned_data['disability']
        user.dietary = self.cleaned_data['dietary']
        user.save()
        return user