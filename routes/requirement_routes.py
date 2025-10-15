#this contains the code that fulfills the rest of the requirements
"""
Library Management System - Business Logic Functions
Complete implementation of R3-R7 requirements
"""

from datetime import datetime, timedelta
import database as db


# R3: Book Borrowing Interface (Complete implementation)
def borrow_book(patron_id, book_id):
    """
    Process a book borrowing request.
    
    Args:
        patron_id (str): Patron identification number
        book_id (int): Book ID from catalog
        
    Returns:
        dict: {'success': bool, 'message': str, 'due_date': str (optional)}
    """
    # Validate patron ID format (assuming alphanumeric, 5-10 characters)
    if not patron_id or not isinstance(patron_id, str):
        return {'success': False, 'message': 'Invalid patron ID format'}
    
    if len(patron_id) < 5 or len(patron_id) > 10:
        return {'success': False, 'message': 'Patron ID must be 5-10 characters'}
    
    # Check if book exists and is available
    book = db.get_book_by_id(book_id)
    if not book:
        return {'success': False, 'message': 'Book not found'}
    
    if book['available_copies'] <= 0:
        return {'success': False, 'message': 'Book is not available'}
    
    # Check patron's current borrowed books (limit: 5 books)
    current_borrows = db.get_patron_active_borrows(patron_id)
    MAX_BORROWS = 5
    
    if len(current_borrows) >= MAX_BORROWS:
        return {'success': False, 'message': f'Borrowing limit reached ({MAX_BORROWS} books)'}
    
    # Check if patron already has this book borrowed
    for borrow in current_borrows:
        if borrow['book_id'] == book_id:
            return {'success': False, 'message': 'You have already borrowed this book'}
    
    # Process the borrowing
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    success = db.create_borrow_record(patron_id, book_id, borrow_date, due_date)
    
    if success:
        db.update_book_availability(book_id, book['available_copies'] - 1)
        return {
            'success': True, 
            'message': 'Book borrowed successfully',
            'due_date': due_date
        }
    else:
        return {'success': False, 'message': 'Failed to process borrowing'}


# R4: Book Return Processing
def return_book(patron_id, book_id):
    """
    Process a book return.
    
    Args:
        patron_id (str): Patron identification number
        book_id (int): Book ID being returned
        
    Returns:
        dict: {'success': bool, 'message': str, 'late_fee': float (optional)}
    """
    # Validate inputs
    if not patron_id or not isinstance(patron_id, str):
        return {'success': False, 'message': 'Invalid patron ID'}
    
    # Find the active borrow record
    borrow_record = db.get_active_borrow(patron_id, book_id)
    
    if not borrow_record:
        return {'success': False, 'message': 'No active borrow record found'}
    
    # Calculate late fee if overdue
    return_date = datetime.now().strftime('%Y-%m-%d')
    due_date = datetime.strptime(borrow_record['due_date'], '%Y-%m-%d')
    return_datetime = datetime.strptime(return_date, '%Y-%m-%d')
    
    late_fee = 0.0
    if return_datetime > due_date:
        days_late = (return_datetime - due_date).days
        late_fee = days_late * 0.50  # $0.50 per day late fee
    
    # Update borrow record with return date
    success = db.update_borrow_return_date(borrow_record['id'], return_date)
    
    if success:
        # Update book availability
        book = db.get_book_by_id(book_id)
        db.update_book_availability(book_id, book['available_copies'] + 1)
        
        response = {
            'success': True,
            'message': 'Book returned successfully'
        }
        
        if late_fee > 0:
            response['late_fee'] = late_fee
            response['message'] = f'Book returned. Late fee: ${late_fee:.2f}'
        
        return response
    else:
        return {'success': False, 'message': 'Failed to process return'}


# R5: Late Fee Calculation API
def calculate_late_fee(patron_id):
    """
    Calculate total late fees for a patron.
    
    Args:
        patron_id (str): Patron identification number
        
    Returns:
        dict: {'patron_id': str, 'total_late_fee': float, 'overdue_books': list}
    """
    if not patron_id or not isinstance(patron_id, str):
        return {'error': 'Invalid patron ID'}
    
    active_borrows = db.get_patron_active_borrows(patron_id)
    
    if not active_borrows:
        return {
            'patron_id': patron_id,
            'total_late_fee': 0.0,
            'overdue_books': []
        }
    
    current_date = datetime.now()
    total_late_fee = 0.0
    overdue_books = []
    
    for borrow in active_borrows:
        due_date = datetime.strptime(borrow['due_date'], '%Y-%m-%d')
        
        if current_date > due_date:
            days_late = (current_date - due_date).days
            late_fee = days_late * 0.50
            total_late_fee += late_fee
            
            book = db.get_book_by_id(borrow['book_id'])
            overdue_books.append({
                'book_id': borrow['book_id'],
                'title': book['title'] if book else 'Unknown',
                'days_late': days_late,
                'late_fee': late_fee
            })
    
    return {
        'patron_id': patron_id,
        'total_late_fee': round(total_late_fee, 2),
        'overdue_books': overdue_books
    }


# R6: Book Search Functionality
def search_books(query, search_type='all'):
    """
    Search for books by title, author, or ISBN.
    
    Args:
        query (str): Search query string
        search_type (str): 'title', 'author', 'isbn', or 'all'
        
    Returns:
        list: List of matching books
    """
    if not query or not isinstance(query, str):
        return []
    
    query = query.strip().lower()
    
    if len(query) < 2:
        return []
    
    all_books = db.get_all_books()
    results = []
    
    for book in all_books:
        match = False
        
        if search_type in ['title', 'all']:
            if query in book['title'].lower():
                match = True
        
        if search_type in ['author', 'all']:
            if query in book['author'].lower():
                match = True
        
        if search_type in ['isbn', 'all']:
            if query in book['isbn'].lower():
                match = True
        
        if match and book not in results:
            results.append(book)
    
    # Sort results by title
    results.sort(key=lambda x: x['title'])
    
    return results


# R7: Patron Status Report
def get_patron_status(patron_id):
    """
    Generate a comprehensive status report for a patron.
    
    Args:
        patron_id (str): Patron identification number
        
    Returns:
        dict: Comprehensive patron status including borrowed books, fees, etc.
    """
    if not patron_id or not isinstance(patron_id, str):
        return {'error': 'Invalid patron ID'}
    
    # Get active borrows
    active_borrows = db.get_patron_active_borrows(patron_id)
    
    # Get borrow history
    borrow_history = db.get_patron_borrow_history(patron_id)
    
    # Calculate late fees
    late_fee_info = calculate_late_fee(patron_id)
    
    # Prepare borrowed books list with details
    borrowed_books = []
    for borrow in active_borrows:
        book = db.get_book_by_id(borrow['book_id'])
        due_date = datetime.strptime(borrow['due_date'], '%Y-%m-%d')
        current_date = datetime.now()
        
        is_overdue = current_date > due_date
        days_until_due = (due_date - current_date).days
        
        borrowed_books.append({
            'book_id': borrow['book_id'],
            'title': book['title'] if book else 'Unknown',
            'author': book['author'] if book else 'Unknown',
            'borrow_date': borrow['borrow_date'],
            'due_date': borrow['due_date'],
            'is_overdue': is_overdue,
            'days_until_due': days_until_due if not is_overdue else -abs(days_until_due)
        })
    
    # Calculate statistics
    total_books_borrowed = len(borrow_history)
    books_currently_borrowed = len(active_borrows)
    books_returned = total_books_borrowed - books_currently_borrowed
    
    return {
        'patron_id': patron_id,
        'books_currently_borrowed': books_currently_borrowed,
        'borrowing_limit': 5,
        'books_available_to_borrow': 5 - books_currently_borrowed,
        'borrowed_books': borrowed_books,
        'total_late_fees': late_fee_info['total_late_fee'],
        'overdue_books_count': len(late_fee_info['overdue_books']),
        'total_books_ever_borrowed': total_books_borrowed,
        'total_books_returned': books_returned
    }