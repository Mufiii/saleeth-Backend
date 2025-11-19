Book API

Authentication required for all book endpoints.

Endpoints
- GET /books/ — list published books; each includes is_locked
- GET /books/{id}/ — detail; when locked returns preview chapters only and hides content_file
- GET /books/{id}/read/ — returns same detail but 403 if locked (optional)

Lock Logic
- A book is unlocked for a user iff a BookAccess(user, book) exists
- Blocked users (is_blocked=True) receive 403 on all endpoints

Admin
- Use Django admin /admin/ to manage Books and related inlines (Chapters, YouTube links, ToC)
- Manage access by creating BookAccess rows for users and books

