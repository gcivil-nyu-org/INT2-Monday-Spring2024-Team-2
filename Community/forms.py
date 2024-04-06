from django import forms
from TutorRegister.models import Post, Reply


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ["title", "content", "label", "attachment"]

        labels = {
            "title": "Title",
            "content": "Content",
            "label": "Label",
            "attachment": "Attachment",
        }

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
            "label": forms.RadioSelect,
            "attachment": forms.FileInput(attrs={"class": "form-control-file"}),
        }

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)

        self.fields["label"].choices = [
            ("resource", "Resource"),
            ("question", "Question"),
        ]


class CreateReplyForm(forms.ModelForm):
    class Meta:
        model = Reply

        fields = ["content"]

        labels = {"content": "Content"}

        widgets = {"content": forms.Textarea(attrs={"class": "form-control"})}
