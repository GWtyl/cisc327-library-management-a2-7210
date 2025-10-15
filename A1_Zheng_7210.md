Name: Joshua Zheng
R1: Add Book To Catalog | Title: complete | Author complete| IBSN: complete | total copies: complete | display success: complete|
---------------------------------------------------------------------------------------------------------------------------------
R2: Book Catalog Display | correct order: complete | available/total copies: complete | actions: complete |
---------------------------------------------------------------------------------------------------------------------------------
R3: Book Borrowing Interface | Valid ID: complete | Checks book availability and patron borrowing limits : Partial |            Displays appropriate success/error messages: complete
---------------------------------------------------------------------------------------------------------------------------------
R4:  Book Return Processing | not implemented
---------------------------------------------------------------------------------------------------------------------------------
R5: Late Fee Calculation API | not implemented
---------------------------------------------------------------------------------------------------------------------------------
R6: Book Search Functionality | not implemented
---------------------------------------------------------------------------------------------------------------------------------
R7: Patron Status Report | not implemented
---------------------------------------------------------------------------------------------------------------------------------
test cases:
add_book_to_catalog - Contains 4 tests for add_book_to_catalog, covering valid input, invalid ISBN, duplicate ISBN, and invalid total copies.
borrow_book_by_patron - Contains 5 tests for borrow_book_by_patron, covering valid borrow, invalid patron ID, book not found, unavailable book, and borrowing limit reached.
calculate_late_fee_for_book - Contains 4 tests for return_book_by_patron. Since the function is not yet implemented, tests check placeholder behavior.
get_patron_status_report - Contains 4 tests for calculate_late_fee_for_book. Tests ensure dict structure, default values, and placeholder status.
return_book_by_patron - Contains 4 tests for search_books_in_catalog, verifying placeholder return behavior.
search_books_in_catalog - Contains 4 tests for get_patron_status_report, verifying placeholder return behavior.