import os
import tempfile
import unittest
from unittest.mock import patch

from app import app, create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        env = patch.dict(
            os.environ,
            {"ADMIN_PASSWORD": "test-password", "SECRET_KEY": "test-secret"},
        )
        env.start()
        self.addCleanup(env.stop)
        database_url = f"sqlite:///{self.temp_dir.name}/test.db"
        self.flask_app = create_app(database_url)
        self.flask_app.config["TESTING"] = True
        self.client = self.flask_app.test_client()
        self.addCleanup(self.temp_dir.cleanup)

    def test_root_is_a_wsgi_app(self):
        self.assertIsNotNone(app.wsgi_app)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_signup_validation_and_submission(self):
        invalid_response = self.client.post("/", data={"hero_name": ""})
        self.assertEqual(invalid_response.status_code, 400)
        self.assertIn(b"Hero name is required", invalid_response.data)

        response = self.client.post(
            "/",
            data={
                "hero_name": "Test Hero",
                "powers": "Flight",
                "age": "25",
                "location": "HQ",
                "email": "hero@example.com",
            },
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["Location"], "/?success=1")

    def test_admin_authentication_and_csv_export(self):
        response = self.client.get("/admin/export")
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            "/admin", data={"password": "test-password"}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Applications Review", response.data)

        response = self.client.get("/admin/export")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn(b"id,hero_name,powers,age,location,email", response.data)

    def test_vercel_uses_writable_sqlite_copy(self):
        sqlite_path = os.path.join(self.temp_dir.name, "vercel", "heroes.db")
        with (
            patch.dict(os.environ, {"VERCEL": "1"}, clear=False),
            patch.dict(os.environ, {"DATABASE_URL": ""}),
        ):
            vercel_app = create_app(sqlite_path=sqlite_path)
            vercel_app.config["TESTING"] = True
            response = vercel_app.test_client().get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.isfile(sqlite_path))


if __name__ == "__main__":
    unittest.main()
