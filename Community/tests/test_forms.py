from django.test import TestCase
from Community.forms import CreatePostForm, CreateReplyForm


class CreatePostFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            "title": "Test title",
            "content": "Test content",
            "label": "resource",
        }

        form = CreatePostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            "title": "Test title",
            "content": "Test content",
        }

        form = CreatePostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("label", form.errors)


class CreateReplyFormTest(TestCase):
    def test_valid_form(self):
        form_data = {"content": "Test reply"}

        form = CreateReplyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {"content": ""}

        form = CreateReplyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)
