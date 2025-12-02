import subprocess
import time
import pytest
import uuid
import random
import requests
from flask import url_for
import pytest
from playwright.sync_api import Page, expect
    
@pytest.fixture(scope="session", autouse=True)
def flask_server():
    """Start the Flask app in a subprocess for the entire test session."""
    proc = subprocess.Popen(["python", "app.py"])
    
    # Wait for Flask to be up
    for _ in range(20):  # 20 * 0.5s = 10s max
        try:
            r = requests.get("http://127.0.0.1:5000")
            if r.status_code == 200:
                break
        except:
            time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError("Flask server did not start in time")
    
    yield  # tests run here
    
    # Teardown: stop Flask
    proc.terminate()
    proc.wait()


"""Realistic User Flow 1: Librarian adds a new book to the catalog"""
def test_user_flow_librarian_adds_new_book_to_catalog(page: Page):

    # Generate unique book data to avoid conflicts
    uid = uuid.uuid4().hex[:10]
    book_title = f"The Midnight Library {uid}"
    author_name = f"Matt Haig {uid}"
    isbn = ''.join(random.choices("0123456789", k=13))
    copies = "5"
    
    # Step 1: Navigate to catalog
    page.goto("http://127.0.0.1:5000")
    page.get_by_role("link", name="📖 Catalog").click()
    expect(page).to_have_url("http://127.0.0.1:5000/catalog")
    
    # Step 2: Click "Add Book" button
    page.get_by_role("link", name="➕ Add Book").click()
    expect(page).to_have_url("http://127.0.0.1:5000/add_book")
    
    # Step 3: Fill in the book details
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill(book_title)
    
    page.get_by_role("textbox", name="Author *").click()
    page.get_by_role("textbox", name="Author *").fill(author_name)
    
    page.get_by_role("textbox", name="ISBN *").click()
    page.get_by_role("textbox", name="ISBN *").fill(isbn)
    
    page.get_by_role("spinbutton", name="Total Copies *").click()
    page.get_by_role("spinbutton", name="Total Copies *").fill(copies)
    
    # Step 4: Submit the form
    page.get_by_role("button", name="Add Book to Catalog").click()
    
    # Step 5: Verify success by checking redirect to catalog
    expect(page).to_have_url("http://127.0.0.1:5000/catalog")
    
    # Step 6 & 7: Verify the book appears with correct details
    expect(page.get_by_role("cell", name=book_title)).to_be_visible()
    expect(page.get_by_role("cell", name=author_name)).to_be_visible()
    expect(page.get_by_role("cell", name=isbn)).to_be_visible()
    
    # Verify the available copies
    book_row = page.locator(f'tr:has-text("{book_title}")')
    expect(book_row).to_be_visible()
    expect(book_row).to_contain_text(copies)


""" 
Realistic User Flow 2: Patron browses catalog and borrows a book 
    Steps:
    1. Navigate to catalog page
    2. Browse available books
    3. Enter patron ID
    4. Click "Borrow" button for a specific book
    5. Verify success by checking redirect to catalog
    6. Search for the borrowed book
    7. Verify available copies decreased
"""
def test_user_flow_patron_browses_and_borrows_book(page: Page):
    # Generate unique data
    uid = uuid.uuid4().hex[:10]
    book_title = f"Project Hail Mary {uid}"
    author_name = f"Andy Weir {uid}"
    isbn = ''.join(random.choices("0123456789", k=13))
    patron_id = ''.join(random.choices("0123456789", k=6))
    initial_copies = "3"
    
    # First, add a book that we can borrow
    page.goto("http://127.0.0.1:5000/add_book")
    page.get_by_role("textbox", name="Title *").fill(book_title)
    page.get_by_role("textbox", name="Author *").fill(author_name)
    page.get_by_role("textbox", name="ISBN *").fill(isbn)
    page.get_by_role("spinbutton", name="Total Copies *").fill(initial_copies)
    page.get_by_role("button", name="Add Book to Catalog").click()
    
    # Step 1: Navigate to catalog
    page.goto("http://127.0.0.1:5000")
    page.get_by_role("link", name="📖 Catalog").click()
    expect(page).to_have_url("http://127.0.0.1:5000/catalog")
    
    # Step 2: Browse and verify the book is available
    expect(page.get_by_role("cell", name=book_title)).to_be_visible()
    expect(page.get_by_role("cell", name=author_name)).to_be_visible()
    
    # Verify initial available copies
    book_row = page.locator(f'tr:has-text("{book_title}")')
    expect(book_row).to_be_visible()
    expect(book_row).to_contain_text("3")
    
    # Step 3: Enter patron ID
    patron_input = book_row.get_by_role("textbox", name="Patron ID")
    expect(patron_input).to_be_visible()
    patron_input.click()
    patron_input.fill(patron_id)
    
    # Step 4: Click "Borrow" button
    borrow_button = book_row.get_by_role("button", name="Borrow")
    expect(borrow_button).to_be_visible()
    expect(borrow_button).to_be_enabled()
    borrow_button.click()
    
    # Step 5: Verify success by checking redirect to catalog
    expect(page).to_have_url("http://127.0.0.1:5000/catalog")
    
    # Step 6: Search for the borrowed book to verify changes
    page.get_by_role("link", name="🔍 Search").click()
    page.get_by_role("textbox", name="Search Term").click()
    page.get_by_role("textbox", name="Search Term").fill(book_title)
    page.get_by_role("button", name="🔍 Search").click()
    
    # Step 7: Verify the book appears and available copies decreased
    expect(page.get_by_role("cell", name=book_title)).to_be_visible()
    
    # Verify available copies decreased from 3 to 2
    book_row = page.locator(f'tr:has-text("{book_title}")')
    expect(book_row).to_be_visible()
    expect(book_row).to_contain_text("2")  # Should show 2 available now
