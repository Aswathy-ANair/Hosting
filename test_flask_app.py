import unittest
from app import app

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        # Propagate exceptions to the test client
        self.app.testing = True

    def test_index_route(self):
        # Send a GET request to the /index route
        response = self.app.get('/index')
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_login_route(self):
        # Send a GET request to the /login route
        response = self.app.get('/login')
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_add_games_route(self):
        # Send a GET request to the /add_games route
        response = self.app.get('/add_games')
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    # Add more test methods for other routes as needed

if __name__ == '__main__':
    unittest.main()
