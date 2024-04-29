from django.test import TestCase, Client, RequestFactory
from TutorRegister.models import Post, Reply, Vote
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache


class ViewAllPostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # self.factory = RequestFactory()
        self.tutor = User.objects.get(pk=cache.get("tutor"))
        self.student = User.objects.get(pk=cache.get("student"))
        self.client.login(username="test@example.com", password="testpassword")
        self.post = Post.objects.create(
            user=self.tutor,
            label="resource",
            title="Test title",
            content="Test content",
            topics="math",
        )

    def test_view_all_posts(self):
        url = reverse("Community:all_posts")
        response = self.client.get(url)

        self.assertEqual(len(response.context["posts"]), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts.html")

    def test_search_posts(self):
        url = reverse("Community:all_posts")
        response = self.client.get(url, {"search": "content"})

        self.assertEqual(len(response.context["posts"]), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts.html")

    def test_filter_posts(self):
        url = reverse("Community:all_posts")
        response = self.client.get(url, {"label": "resource", "topic": "computer_sci"})

        self.assertEqual(len(response.context["posts"]), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts.html")


class ViewPostDetailTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.tutor = User.objects.get(pk=cache.get("tutor"))
        self.student = User.objects.get(pk=cache.get("student"))
        self.client.login(username="test@example.com", password="testpassword")
        self.post = Post.objects.create(
            user=self.tutor,
            label="resource",
            title="Test title",
            content="Test content",
        )

    def test_view_post_detail(self):
        url = reverse("Community:post_detail", args=[self.post.id])

        reply_data = {
            "content": "Test reply.",
            "post_id": self.post.id,
        }
        response = self.client.post(url, reply_data, follow=True)

        self.assertRedirects(
            response,
            url,
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            Reply.objects.filter(post=self.post, user=self.student).exists()
        )


class CreatePostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.get(pk=cache.get("student"))
        self.client.login(username="test@example.com", password="testpassword")

    def test_create_post_view(self):
        url = reverse("Community:create_post")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_post.html")

    def test_create_post_submit(self):
        url = reverse("Community:create_post")
        redirect_url = reverse("Community:all_posts")
        post_form = {
            "label": "question",
            "title": "Test title",
            "content": "Test question content",
        }
        response = self.client.post(url, post_form, follow=True)

        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Post.objects.filter(user=self.student).exists())


class EditDeleteVotePostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.get(pk=cache.get("student"))
        self.client.login(username="test@example.com", password="testpassword")
        self.post = Post.objects.create(
            user=self.student,
            label="resource",
            title="Test title",
            content="Test content",
            topics="math",
        )

    def test_edit_post(self):
        url = reverse("Community:edit", kwargs={"post_id": self.post.id})
        redirect_url = reverse(
            "Community:post_detail", kwargs={"post_id": self.post.id}
        )

        post_form = {
            "label": "question",
            "title": "Test title",
            "content": "Test question content",
            "topics": "computer_sci",
        }

        response = self.client.post(url, post_form, follow=True)
        self.post.refresh_from_db()

        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(self.post.content, "Test question content")

    def test_delete_post(self):
        url = reverse("Community:delete_post", kwargs={"post_id": self.post.id})
        response = self.client.post(url, follow=True)

        self.assertTrue(response.json()["success"])
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_vote_post(self):
        url = reverse(
            "Community:vote", kwargs={"post_id": self.post.id, "vote_type": "downvote"}
        )
        response = self.client.get(url)

        self.post.refresh_from_db()

        self.assertTrue(Vote.objects.filter(post=self.post, user=self.student).exists())
        self.assertEqual(self.post.get_rating(), -1)
        self.assertEqual(
            response.json(), {"upvotes_count": 0, "downvotes_count": 1, "user_vote": -1}
        )
