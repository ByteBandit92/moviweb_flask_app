import unittest
from flask import Flask
from app import app, data_manager  # assuming your Flask app is in app.py
from unittest.mock import patch

class TestApp(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock data manager methods if needed (e.g., SQLiteDataManager)
        self.mock_data_manager = patch.object(data_manager, 'get_all_users', return_value=[])
        self.mock_data_manager.start()

    def tearDown(self):
        # Stop the mocking
        self.mock_data_manager.stop()


    def test_add_user_get(self):
        response = self.app.get('/add_user')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add User', response.data)  # Assuming the form contains this text

    def test_add_user_post(self):
        with patch('datamanager.sqlite_data_manager.SQLiteDataManager.add_user') as mock_add_user:
            response = self.app.post('/add_user', data={'name': 'New User'})
            self.assertEqual(response.status_code, 302)  # Redirects to /users
            mock_add_user.assert_called_once_with('New User')

    def test_add_movie_post(self):
        with patch('requests.get') as mock_get, \
             patch('datamanager.sqlite_data_manager.SQLiteDataManager.add_movie') as mock_add_movie:
            
            mock_get.return_value.json.return_value = {
                'Response': 'True',
                'Title': 'New Movie',
                'Director': 'Director Name',
                'Year': '2025',
                'imdbRating': '7.5'
            }
            
            response = self.app.post('/users/1/add_movie', data={'name': 'New Movie'})
            self.assertEqual(response.status_code, 302)  # Redirects to user movies page
            mock_add_movie.assert_called_once_with(1, 'New Movie', 'Director Name', 2025, 7.5)

    def test_update_movie_get(self):
        # Assuming movie_id 1 exists
        with patch('datamanager.sqlite_data_manager.SQLiteDataManager.get_movie', return_value={'id': 1, 'name': 'Old Movie'}):
            response = self.app.get('/users/1/update_movie/1')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Old Movie', response.data)

    def test_update_movie_post(self):
        with patch('datamanager.sqlite_data_manager.SQLiteDataManager.update_movie') as mock_update_movie:
            response = self.app.post('/users/1/update_movie/1', data={'name': 'Updated Movie', 'director': 'New Director', 'year': '2026', 'rating': '8.0'})
            self.assertEqual(response.status_code, 302)  # Redirects to user movies page
            mock_update_movie.assert_called_once()

    def test_delete_movie(self):
        with patch('datamanager.sqlite_data_manager.SQLiteDataManager.delete_movie') as mock_delete_movie:
            response = self.app.get('/users/1/delete_movie/1')
            self.assertEqual(response.status_code, 302)  # Redirects to user movies page
            mock_delete_movie.assert_called_once_with(1)

    def test_page_not_found(self):
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)  # Assuming the 404.html has this text

if __name__ == '__main__':
    unittest.main()
