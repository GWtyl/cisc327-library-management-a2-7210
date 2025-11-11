"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books,
    get_borrow_record_by_patron_and_book, get_all_patron_borrow_records
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4: Book Return Processing
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Verify the book was borrowed by this patron
    borrow_record = get_borrow_record_by_patron_and_book(patron_id, book_id)
    if not borrow_record:
        return False, "No active borrow record found for this book and patron."
    
    # Update return date
    return_date = datetime.now()
    return_success = update_borrow_record_return_date(borrow_record['id'], return_date)
    if not return_success:
        return False, "Database error occurred while recording return."
    
    # Update available copies
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    # Calculate late fees if applicable
    due_date = borrow_record['due_date']
    if isinstance(due_date, str):
        due_date = datetime.fromisoformat(due_date)
    
    late_fee = 0.0
    if return_date > due_date:
        days_overdue = (return_date - due_date).days
        
        # Calculate fee based on requirements
        if days_overdue <= 7:
            late_fee = days_overdue * 0.50
        else:
            # First 7 days at $0.50/day
            late_fee = 7 * 0.50
            # Additional days at $1.00/day
            late_fee += (days_overdue - 7) * 1.00
        
        # Cap at $15.00
        late_fee = min(late_fee, 15.00)
        
        return True, f'Book "{book["title"]}" returned successfully. Late fee: ${late_fee:.2f} ({days_overdue} days overdue).'
    else:
        return True, f'Book "{book["title"]}" returned successfully. No late fees.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5: Late Fee Calculation API
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book
        
    Returns:
        dict: Contains fee_amount, days_overdue, and status
    """
    # Get the borrow record
    borrow_record = get_borrow_record_by_patron_and_book(patron_id, book_id)
    
    if not borrow_record:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No active borrow record found'
        }
    
    # If already returned, no late fee calculation needed
    if borrow_record.get('return_date'):
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book already returned'
        }
    
    # Calculate days overdue
    due_date = borrow_record['due_date']
    if isinstance(due_date, str):
        due_date = datetime.fromisoformat(due_date)
    
    current_date = datetime.now()
    
    if current_date <= due_date:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Not overdue'
        }
    
    days_overdue = (current_date - due_date).days
    
    # Calculate fee
    if days_overdue <= 7:
        fee = days_overdue * 0.50
    else:
        # First 7 days at $0.50/day
        fee = 7 * 0.50
        # Additional days at $1.00/day
        fee += (days_overdue - 7) * 1.00
    
    # Cap at $15.00
    fee = min(fee, 15.00)
    
    return {
        'fee_amount': round(fee, 2),
        'days_overdue': days_overdue,
        'status': 'Overdue'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6: Book Search Functionality
    
    Args:
        search_term: The term to search for
        search_type: Type of search ('title', 'author', or 'isbn')
        
    Returns:
        list: List of matching books in the same format as catalog
    """
    if not search_term or not search_term.strip():
        return []
    
    if search_type not in ['title', 'author', 'isbn']:
        return []
    
    # Get all books from catalog
    all_books = get_all_books()
    
    if not all_books:
        return []
    
    search_term = search_term.strip()
    results = []
    
    for book in all_books:
        if search_type == 'isbn':
            # ISBN: Exact matching
            if book['isbn'] == search_term:
                results.append(book)
        elif search_type == 'title':
            # Title: Partial matching, case-insensitive
            if search_term.lower() in book['title'].lower():
                results.append(book)
        elif search_type == 'author':
            # Author: Partial matching, case-insensitive
            if search_term.lower() in book['author'].lower():
                results.append(book)
    
    return results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7: Patron Status Report
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: Status report with borrowed books, fees, and history
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'error': 'Invalid patron ID'
        }
    
    # Get all borrow records for this patron
    borrow_records = get_all_patron_borrow_records(patron_id)
    
    currently_borrowed = []
    borrowing_history = []
    total_late_fees = 0.0
    
    current_date = datetime.now()
    
    for record in borrow_records:
        book = get_book_by_id(record['book_id'])
        
        if not book:
            continue
        
        due_date = record['due_date']
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
        
        # Check if currently borrowed (no return date)
        if not record.get('return_date'):
            # Calculate late fee if overdue
            late_fee = 0.0
            if current_date > due_date:
                days_overdue = (current_date - due_date).days
                if days_overdue <= 7:
                    late_fee = days_overdue * 0.50
                else:
                    late_fee = 7 * 0.50 + (days_overdue - 7) * 1.00
                late_fee = min(late_fee, 15.00)
                total_late_fees += late_fee
            
            currently_borrowed.append({
                'book_id': book['id'],
                'title': book['title'],
                'author': book['author'],
                'due_date': due_date.strftime("%Y-%m-%d"),
                'late_fee': round(late_fee, 2)
            })
        
        # Add to history
        borrow_date = record['borrow_date']
        if isinstance(borrow_date, str):
            borrow_date = datetime.fromisoformat(borrow_date)
        
        history_entry = {
            'book_id': book['id'],
            'title': book['title'],
            'author': book['author'],
            'borrow_date': borrow_date.strftime("%Y-%m-%d"),
            'due_date': due_date.strftime("%Y-%m-%d")
        }
        
        if record.get('return_date'):
            return_date = record['return_date']
            if isinstance(return_date, str):
                return_date = datetime.fromisoformat(return_date)
            history_entry['return_date'] = return_date.strftime("%Y-%m-%d")
        
        borrowing_history.append(history_entry)
    
    return {
        'patron_id': patron_id,
        'currently_borrowed': currently_borrowed,
        'num_books_borrowed': len(currently_borrowed),
        'total_late_fees': round(total_late_fees, 2),
        'borrowing_history': borrowing_history
    }