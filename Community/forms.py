from typing import Any
from django import forms
from TutorRegister.models import Post, Reply
from TutorRegister.presets import EXPERTISE_CHOICES


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ["title", "content", "label", "attachment", "topics"]

        labels = {
            "title": "Title",
            "content": "Content",
            "label": "Label",
            "attachment": "Attachment",
            "topics": "Topic",
        }

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
            "label": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "attachment": forms.FileInput(attrs={"class": "form-control-file"}),
            "topics": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)

        self.fields["label"].choices = [
            ("resource", "Resource"),
            ("question", "Question"),
        ]

        self.fields["topics"] = forms.ChoiceField(
            choices=EXPERTISE_CHOICES,
            widget=self.Meta.widgets["topics"],
            required=False,
        )


class CreateReplyForm(forms.ModelForm):
    class Meta:
        model = Reply

        fields = ["content"]

        labels = {"content": "Content"}

        widgets = {"content": forms.Textarea(attrs={"class": "form-control"})}


class SearchFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        max_length=320,
        widget=forms.TextInput(attrs={"placeholder": "Search posts..."}),
    )
    label = forms.ChoiceField(
        required=False,
        choices=[("", "None"), ("resource", "Resource"), ("question", "Question")],
        label="Label",
    )
    topic = forms.ChoiceField(
        required=False, choices=[("", "None")] + EXPERTISE_CHOICES, label="Topic"
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("", "None"),
            ("highest_rating", "Highest Rating"),
            ("most_viewed", "Most Viewed"),
            ("earliest_post", "Earliest Post"),
        ],
        label="Sort",
    )

    def clean(self):
        cleaned_data = super().clean()

        for key in cleaned_data:
            value = cleaned_data[key]
            if isinstance(value, str):
                cleaned_data[key] = value.strip()
            if not value:
                cleaned_data[key] = None

        return cleaned_data
