"""
Comprehensive Test Suite for Library Management System
Tests for R3-R7 requirements
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import services.library_service as ls


class TestBorrowBook(unittest.TestCase):
    """Test cases for R3: Book Borrowing Interface"""
    
    @patch('library_service.db')
    def test_borrow_book_success(self, mock_db):
        """Test successful book borrowing with valid inputs"""
        # Setup
        mock_db.get_book_by_id.return_value = {
            'id': 1,
            'title': 'Python Programming',
            'author': 'John Doe',
            'isbn': '978-0-123456-78-9',
            'available_copies': 3
        }
        mock_db.get_patron_active_borrows.return_value = []
        mock_db.create_borrow_record.return_value = True
        
        # Execute
        result = ls.borrow_book('PAT12345', 1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Book borrowed successfully')
        self.assertIn('due_date', result)
        mock_db.update_book_availability.assert_called_once_with(1, 2)
    
    @patch('library_service.db')
    def test_borrow_book_invalid_patron_id(self, mock_db):
        """Test borrowing with invalid patron ID format"""
        # Test empty patron ID
        result = ls.borrow_book('', 1)
        self.assertFalse(result['success'])
        self.assertIn('Invalid patron ID', result['message'])
        
        # Test too short patron ID
        result = ls.borrow_book('PAT1', 1)
        self.assertFalse(result['success'])
        self.assertIn('5-10 characters', result['message'])
        
        # Test too long patron ID
        result = ls.borrow_book('PAT12345678901', 1)
        self.assertFalse(result['success'])
    
    @patch('library_service.db')
    def test_borrow_book_not_available(self, mock_db):
        """Test borrowing when book has no available copies"""
        mock_db.get_book_by_id.return_value = {
            'id': 1,
            'title': 'Python Programming',
            'available_copies': 0
        }
        
        result = ls.borrow_book('PAT12345', 1)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Book is not available')
    
    @patch('library_service.db')
    def test_borrow_book_borrowing_limit_reached(self, mock_db):
        """Test borrowing when patron has reached maximum borrowing limit"""
        mock_db.get_book_by_id.return_value = {
            'id': 6,
            'available_copies': 2
        }
        # Patron already has 5 books borrowed
        mock_db.get_patron_active_borrows.return_value = [
            {'book_id': 1}, {'book_id': 2}, {'book_id': 3},
            {'book_id': 4}, {'book_id': 5}
        ]
        
        result = ls.borrow_book('PAT12345', 6)
        
        self.assertFalse(result['success'])
        self.assertIn('Borrowing limit reached', result['message'])


class TestReturnBook(unittest.TestCase):
    """Test cases for R4: Book Return Processing"""
    
    @patch('library_service.db')
    @patch('library_service.datetime')
    def test_return_book_on_time(self, mock_datetime, mock_db):
        """Test returning a book before due date (no late fee)"""
        # Setup
        current_date = datetime(2025, 10, 10)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime = datetime.strptime
        
        mock_db.get_active_borrow.return_value = {
            'id': 1,
            'patron_id': 'PAT12345',
            'book_id': 1,
            'due_date': '2025-10-15'
        }
        mock_db.get_book_by_id.return_value = {
            'id': 1,
            'available_copies': 2
        }
        mock_db.update_borrow_return_date.return_value = True
        
        # Execute
        result = ls.return_book('PAT12345', 1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Book returned successfully')
        self.assertNotIn('late_fee', result)
        mock_db.update_book_availability.assert_called_once_with(1, 3)
    
    @patch('library_service.db')
    @patch('library_service.datetime')
    def test_return_book_late(self, mock_datetime, mock_db):
        """Test returning a book after due date (with late fee)"""
        # Setup - 5 days late
        current_date = datetime(2025, 10, 20)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime = datetime.strptime
        
        mock_db.get_active_borrow.return_value = {
            'id': 1,
            'patron_id': 'PAT12345',
            'book_id': 1,
            'due_date': '2025-10-15'
        }
        mock_db.get_book_by_id.return_value = {
            'id': 1,
            'available_copies': 2
        }
        mock_db.update_borrow_return_date.return_value = True
        
        # Execute
        result = ls.return_book('PAT12345', 1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['late_fee'], 2.50)  # 5 days * $0.50
        self.assertIn('Late fee', result['message'])
    
    @patch('library_service.db')
    def test_return_book_no_active_borrow(self, mock_db):
        """Test returning a book with no active borrow record"""
        mock_db.get_active_borrow.return_value = None
        
        result = ls.return_book('PAT12345', 1)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'No active borrow record found')
    
    @patch('library_service.db')
    def test_return_book_invalid_patron_id(self, mock_db):
        """Test return with invalid patron ID"""
        result = ls.return_book('', 1)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid patron ID')


class TestCalculateLateFee(unittest.TestCase):
    """Test cases for R5: Late Fee Calculation API"""
    
    @patch('library_service.db')
    @patch('library_service.datetime')
    def test_calculate_late_fee_with_overdue_books(self, mock_datetime, mock_db):
        """Test late fee calculation with multiple overdue books"""
        # Setup - current date is 5 days after due date for one book
        current_date = datetime(2025, 10, 20)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime = datetime.strptime
        
        mock_db.get_patron_active_borrows.return_value = [
            {'book_id': 1, 'due_date': '2025-10-15'},  # 5 days late
            {'book_id': 2, 'due_date': '2025-10-18'},  # 2 days late
            {'book_id': 3, 'due_date': '2025-10-25'}   # Not late
        ]
        
        mock_db.get_book_by_id.side_effect = [
            {'title': 'Book 1'},
            {'title': 'Book 2'},
            {'title': 'Book 3'}
        ]
        
        # Execute
        result = ls.calculate_late_fee('PAT12345')
        
        # Assert
        self.assertEqual(result['patron_id'], 'PAT12345')
        self.assertEqual(result['total_late_fee'], 3.50)  # (5 * 0.50) + (2 * 0.50)
        self.assertEqual(len(result['overdue_books']), 2)
    
    @patch('library_service.db')
    def test_calculate_late_fee_no_overdue_books(self, mock_db):
        """Test late fee calculation with no overdue books"""
        mock_db.get_patron_active_borrows.return_value = []
        
        result = ls.calculate_late_fee('PAT12345')
        
        self.assertEqual(result['total_late_fee'], 0.0)
        self.assertEqual(len(result['overdue_books']), 0)
    
    def test_calculate_late_fee_invalid_patron_id(self):
        """Test late fee calculation with invalid patron ID"""
        result = ls.calculate_late_fee('')
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Invalid patron ID')
    
    @patch('library_service.db')
    @patch('library_service.datetime')
    def test_calculate_late_fee_exact_due_date(self, mock_datetime, mock_db):
        """Test late fee calculation on exact due date (no fee)"""
        current_date = datetime(2025, 10, 15)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime = datetime.strptime
        
        mock_db.get_patron_active_borrows.return_value = [
            {'book_id': 1, 'due_date': '2025-10-15'}
        ]
        
        result = ls.calculate_late_fee('PAT12345')
        
        self.assertEqual(result['total_late_fee'], 0.0)


class TestSearchBooks(unittest.TestCase):
    """Test cases for R6: Book Search Functionality"""
    
    @patch('library_service.db')
    def test_search_books_by_title(self, mock_db):
        """Test searching books by title"""
        mock_db.get_all_books.return_value = [
            {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'isbn': '111'},
            {'id': 2, 'title': 'Java Basics', 'author': 'Jane Smith', 'isbn': '222'},
            {'id': 3, 'title': 'Advanced Python', 'author': 'Bob Wilson', 'isbn': '333'}
        ]
        
        result = ls.search_books('python', 'title')
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all('python' in book['title'].lower() for book in result))
    
    @patch('library_service.db')
    def test_search_books_by_author(self, mock_db):
        """Test searching books by author name"""
        mock_db.get_all_books.return_value = [
            {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'isbn': '111'},
            {'id': 2, 'title': 'Java Basics', 'author': 'John Smith', 'isbn': '222'}
        ]
        
        result = ls.search_books('john', 'author')
        
        self.assertEqual(len(result), 2)
    
    @patch('library_service.db')
    def test_search_books_all_fields(self, mock_db):
        """Test searching across all fields"""
        mock_db.get_all_books.return_value = [
            {'id': 1, 'title': 'Database Systems', 'author': 'Alice Johnson', 'isbn': '978-1234'},
            {'id': 2, 'title': 'Web Development', 'author': 'Bob Smith', 'isbn': '978-5678'}
        ]
        
        result = ls.search_books('978', 'all')
        
        self.assertEqual(len(result), 2)
    
    def test_search_books_empty_query(self):
        """Test search with empty query string"""
        result = ls.search_books('', 'all')
        
        self.assertEqual(len(result), 0)
    
    def test_search_books_short_query(self):
        """Test search with query string too short (< 2 characters)"""
        result = ls.search_books('a', 'all')
        
        self.assertEqual(len(result), 0)


class TestGetPatronStatus(unittest.TestCase):
    """Test cases for R7: Patron Status Report"""
    
    @patch('library_service.db')
    @patch('library_service.datetime')
    @patch('library_service.calculate_late_fee')
    def test_get_patron_status_with_active_borrows(self, mock_calc_fee, mock_datetime, mock_db):
        """Test patron status with active borrowed books"""
        current_date = datetime(2025, 10, 14)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime = datetime.strptime
        
        mock_db.get_patron_active_borrows.return_value = [
            {'book_id': 1, 'borrow_date': '2025-10-01', 'due_date': '2025-10-15'},
            {'book_id': 2, 'borrow_date': '2025-10-05', 'due_date': '2025-10-19'}
        ]
        
        mock_db.get_patron_borrow_history.return_value = [
            {'book_id': 1}, {'book_id': 2}, {'book_id': 3}
        ]
        
        mock_db.get_book_by_id.side_effect = [
            {'title': 'Book 1', 'author': 'Author 1'},
            {'title': 'Book 2', 'author': 'Author 2'}
        ]
        
        mock_calc_fee.return_value = {
            'total_late_fee': 0.0,
            'overdue_books': []
        }
        
        result = ls.get_patron_status('PAT12345')
        
        self.assertEqual(result['patron_id'], 'PAT12345')
        self.assertEqual(result['books_currently_borrowed'], 2)
        self.assertEqual(result['borrowing_limit'], 5)
        self.assertEqual(result['books_available_to_borrow'], 3)
        self.assertEqual(result['total_books_ever_borrowed'], 3)
    
    @patch('library_service.db')
    @patch('library_service.calculate_late_fee')
    def test_get_patron_status_no_active_borrows(self, mock_calc_fee, mock_db):
        """Test patron status with no currently borrowed books"""
        mock_db.get_patron_active_borrows.return_value = []
        mock_db.get_patron_borrow_history.return_value = []
        
        mock_calc_fee.return_value = {
            'total_late_fee': 0.0,
            'overdue_books': []
        }
        
        result = ls.get_patron_status('PAT12345')
        
        self.assertEqual(result['books_currently_borrowed'], 0)
        self.assertEqual(result['books_available_to_borrow'], 5)
    
    def test_get_patron_status_invalid_patron_id(self):
        """Test patron status with invalid patron ID"""
        result = ls.get_patron_status('')
        
        self.assertIn('error', result)
    
    @patch('library_service.db')
    @patch('library_service.datetime')
    @patch('library_service.calculate_late_fee')
    def test_get_patron_status_with_overdue_books(self, mock_calc_fee, mock_datetime, mock_db):
        """Test patron status with overdue books"""
        current_date = datetime(2025, 10, 20)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime = datetime.strptime
        
        mock_db.get_patron_active_borrows.return_value = [
            {'book_id': 1, 'borrow_date': '2025-10-01', 'due_date': '2025-10-15'}
        ]
        
        mock_db.get_patron_borrow_history.return_value = [
            {'book_id': 1}
        ]
        
        mock_db.get_book_by_id.return_value = {
            'title': 'Overdue Book',
            'author': 'Some Author'
        }
        
        mock_calc_fee.return_value = {
            'total_late_fee': 2.50,
            'overdue_books': [{'book_id': 1}]
        }
        
        result = ls.get_patron_status('PAT12345')
        
        self.assertEqual(result['total_late_fees'], 2.50)
        self.assertEqual(result['overdue_books_count'], 1)
        self.assertTrue(result['borrowed_books'][0]['is_overdue'])


if __name__ == '__main__':
    unittest.main()