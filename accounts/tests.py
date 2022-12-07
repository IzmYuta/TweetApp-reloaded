from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        user_data = {
            "username": "test",
            "email": "test@example.com",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        response = self.client.post(self.url, user_data)
        self.assertRedirects(
            response=response,
            status_code=302,
            target_status_code=200,
            expected_url=reverse("tweets:home"),
        )
        self.assertTrue(
            User.objects.filter(username="test", email="test@example.com").exists()
        )

    def test_failure_post_with_empty_form(self):
        user_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="", email="").exists())
        self.assertEqual(form.errors["username"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_username(self):
        user_data = {
            "username": "",
            "email": "test@example.com",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(
            User.objects.filter(username="", email="test@example.com").exists()
        )
        self.assertEqual(form.errors["username"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_email(self):
        user_data = {
            "username": "test",
            "email": "",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_password(self):
        user_data = {
            "username": "test",
            "email": "test@example.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_duplicated_user(self):
        user_data = {
            "username": "test",
            "email": "test@example.com",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        User.objects.create(
            username="test", email="test@example.com", password="goodpass"
        )
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["username"][0], "同じユーザー名が既に登録済みです。")

    def test_failure_post_with_invalid_email(self):
        user_data = {
            "username": "test",
            "email": "test.example.com",
            "password1": "goodpass",
            "password2": "goodpass",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["email"][0], "有効なメールアドレスを入力してください。")

    def test_failure_post_with_too_short_password(self):
        user_data = {
            "username": "test",
            "email": "test@example.com",
            "password1": "pass",
            "password2": "pass",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["password2"][0], "このパスワードは短すぎます。最低 8 文字以上必要です。")

    def test_failure_post_with_password_similar_to_username(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["password2"][0], "このパスワードは ユーザー名 と似すぎています。")

    def test_failure_post_with_only_numbers_password(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "12457836",
            "password2": "12457836",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["password2"][0], "このパスワードは数字しか使われていません。")

    def test_failure_post_with_mismatch_password(self):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "goodpass",
            "password2": "notgoodpass",
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(User.objects.filter(username="test", email="").exists())
        self.assertEqual(form.errors["password2"][0], "確認用パスワードが一致しません。")


class TestLoginView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_user(self):
        pass

    def test_failure_post_with_self(self):
        pass


class TestUnfollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowingListView(TestCase):
    def test_success_get(self):
        pass


class TestFollowerListView(TestCase):
    def test_success_get(self):
        pass
