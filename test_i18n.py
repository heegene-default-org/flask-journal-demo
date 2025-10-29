import unittest
from app import app
import json

class TestFlaskJournalI18n(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_default_language_korean(self):
        """Test that default language is Korean"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # Should contain Korean text by default (checking actual UTF-8 encoded Korean)
        self.assertIn('일기 항목들'.encode('utf-8'), response.data)

    def test_english_language_detection(self):
        """Test English language detection via Accept-Language header"""
        response = self.app.get('/', headers={'Accept-Language': 'en-US,en;q=0.9'})
        self.assertEqual(response.status_code, 200)
        # Should contain English text when Accept-Language is English
        self.assertIn(b'Journal Entries', response.data)

    def test_language_switching(self):
        """Test manual language switching"""
        # Switch to English
        response = self.app.get('/set_language/en')
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that page now displays in English
        response = self.app.get('/')
        self.assertIn(b'Journal Entries', response.data)
        
        # Switch back to Korean
        response = self.app.get('/set_language/ko')
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that page now displays in Korean
        response = self.app.get('/')
        self.assertIn('일기 항목들'.encode('utf-8'), response.data)

    def test_journal_entry_creation(self):
        """Test creating a journal entry"""
        # Set language to English
        self.app.get('/set_language/en')
        
        response = self.app.post('/new', data={
            'title': 'Test Entry',
            'content': 'Test content for the journal entry'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Journal entry created successfully!', response.data)
        self.assertIn(b'Test Entry', response.data)

    def test_new_entry_form_localization(self):
        """Test that the new entry form is properly localized"""
        # Test English form
        self.app.get('/set_language/en')
        response = self.app.get('/new')
        self.assertIn(b'Create New Journal Entry', response.data)
        self.assertIn(b'Title:', response.data)
        self.assertIn(b'Content:', response.data)
        
        # Test Korean form
        self.app.get('/set_language/ko')
        response = self.app.get('/new')
        self.assertIn('새 일기 항목 작성'.encode('utf-8'), response.data)

    def test_missing_fields_validation(self):
        """Test form validation for missing fields"""
        self.app.get('/set_language/en')
        
        # Try to submit form with empty fields
        response = self.app.post('/new', data={
            'title': '',
            'content': ''
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill in both title and content.', response.data)

if __name__ == '__main__':
    unittest.main()