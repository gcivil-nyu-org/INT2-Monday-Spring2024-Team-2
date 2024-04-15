from django import forms
from django.core.validators import RegexValidator


class ContactForm(forms.Form):
    phone_regex = RegexValidator(
        regex=r"^\d{10,15}$",
        message="""Phone number must be entered in the format: '1234567890'\
                 and can be between 10 to 15 digits.""",
    )

    full_name = forms.CharField(
        label="full_name",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "required": True}),
    )

    email = forms.EmailField(
        label="email",
        widget=forms.EmailInput(attrs={"class": "form-control", "required": True}),
    )

    phone = forms.CharField(
        label="phone_number",
        max_length=15,
        required=False,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    message = forms.CharField(
        label="message",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 5, "required": True}
        ),
    )
