from flask import url_for
import pytest
from playwright.sync_api import Page, expect
    
#User Flow 1
def test_user_flow_librarian_adds_new_book_to_catalog(page: Page):
   
    # Step 1: Librarian navigates to add book page
    page.goto("http://localhost:5000/add-book")
    
    # Verify we're on the correct page
    expect(page.locator('h1:has-text("Add New Book")')).to_be_visible()
    
    # Step 2: Librarian fills in the book details
    page.fill('input[name="title"]', 'Test Book')
    page.fill('input[name="author"]', 'Test User')
    page.fill('input[name="isbn"]', '2354596410555')
    page.fill('input[name="total_copies"]', '5')
    
    # Step 3: Librarian submits the form
    page.click('button[type="submit"]')
    
    # Step 4: Verify success message appears
    expect(page.locator('text=successfully added')).to_be_visible()
    expect(page.locator('text=Test Book')).to_be_visible()
    
    # Step 5: Librarian navigates to catalog to verify
    page.goto("http://localhost:5000/catalog")
    
    # Verify catalog page loaded
    expect(page.locator('h1:has-text("Book Catalog")')).to_be_visible()
    
    # Step 6: Verify the book appears in the catalog
    expect(page.locator('text=Test Book')).to_be_visible()
    expect(page.locator('text=Test User')).to_be_visible()
    expect(page.locator('text=2354596410555')).to_be_visible()
    
    # Step 7: Verify available copies shows "5 / 5" or similar format
    book_row = page.locator('tr:has-text("Test Book")')
    expect(book_row).to_be_visible()
    
    # Check that the copies information is displayed
    # This could be "5" or "5/5" or "5 available" depending on your UI
    expect(book_row).to_contain_text('5')
    
    # Verify the borrow button is present and enabled
    borrow_button = book_row.locator('button:has-text("Borrow")')
    expect(borrow_button).to_be_visible()
    expect(borrow_button).to_be_enabled()


#Test 2
def test_user_flow_patron_borrows_book_from_catalog(page: Page):

    # Step 1: Patron navigates to the catalog
    page.goto("http://localhost:5000/catalog")
    
    # Verify catalog page loaded
    expect(page.locator('h1:has-text("Book Catalog")')).to_be_visible()
    
    # Step 2: Patron browses and sees available books
    # Verify the existing book is displayed
    expect(page.locator('text=Existing Book')).to_be_visible()
    expect(page.locator('text=Existing Author')).to_be_visible()
    
    # Verify the book shows as available
    book_row = page.locator('tr:has-text("Existing Book")')
    expect(book_row).to_be_visible()
    
    # Check initial available copies (should be 2)
    expect(book_row).to_contain_text('2')
    
    # Step 3: Patron clicks the "Borrow" button
    borrow_button = book_row.locator('button:has-text("Borrow")')
    expect(borrow_button).to_be_visible()
    expect(borrow_button).to_be_enabled()
    borrow_button.click()
    
    # Should navigate to borrow page or show a form
    # Verify we're on the borrow page or modal appeared
    expect(page.locator('text=Patron ID')).to_be_visible()
    
    # Step 4: Patron enters their library card number
    patron_id_input = page.locator('input[name="patron_id"]')
    expect(patron_id_input).to_be_visible()
    patron_id_input.fill('123456')
    
    # Step 5: Patron submits the borrow request
    submit_button = page.locator('button[type="submit"]')
    submit_button.click()
    
    # Step 6: Verify success confirmation message
    expect(page.locator('text=Successfully borrowed')).to_be_visible()
    expect(page.locator('text=Existing Book')).to_be_visible()
    
    # Verify due date is displayed (14 days from now)
    expect(page.locator('text=Due date')).to_be_visible()
    
    # The confirmation should show the specific due date
    confirmation = page.locator('.alert-success, .success-message, .confirmation')
    expect(confirmation).to_be_visible()
    
    # Step 7: Return to catalog and verify book availability updated
    page.goto("http://localhost:5000/catalog")
    
    # Find the book row again
    book_row = page.locator('tr:has-text("Existing Book")')
    expect(book_row).to_be_visible()
    
    # Verify available copies decreased from 2 to 1
    # Could be displayed as "1 / 2" or just "1 available"
    expect(book_row).to_contain_text('1')
    
    # Verify the borrow button is still present (since 1 copy remains)
    borrow_button = book_row.locator('button:has-text("Borrow")')
    expect(borrow_button).to_be_visible()
    expect(borrow_button).to_be_enabled()
