Name: Joshua Zheng
## Requirements Implementation Status

| Requirement | Feature | Status |
|-------------|---------|--------|
| **R1: Add Book To Catalog** | Title | complete |
| | Author | complete |
| | ISBN | complete |
| | Total copies | complete |
| | Display success | complete |
| **R2: Book Catalog Display** | Correct order | complete |
| | Available/total copies | complete |
| | Actions | complete |
| **R3: Book Borrowing Interface** | Valid ID | complete |
| | Checks book availability and patron borrowing limits | Partial |
| | Displays appropriate success/error messages | complete |
| **R4: Book Return Processing** | | not implemented |
| **R5: Late Fee Calculation API** | | not implemented |
| **R6: Book Search Functionality** | | not implemented |
| **R7: Patron Status Report** | | not implemented |

## Test Cases

| Function | Test Count | Coverage |
|----------|------------|----------|
| **add_book_to_catalog** | 4 tests | Valid input, invalid ISBN, duplicate ISBN, and invalid total copies |
| **borrow_book_by_patron** | 5 tests | Valid borrow, invalid patron ID, book not found, unavailable book, and borrowing limit reached |
| **return_book_by_patron** | 4 tests | Placeholder behavior (function not yet implemented) |
| **calculate_late_fee_for_book** | 4 tests | Dict structure, default values, and placeholder status |
| **search_books_in_catalog** | 4 tests | Placeholder return behavior |
| **get_patron_status_report** | 4 tests | Placeholder return behavior |