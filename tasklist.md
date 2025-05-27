### Important Note: This is a legacy file.

# Clipboard Project Task List

Depends on desired type of artifact (could be either a chrome extension or an local app)

## For local app:
### Clipboard Listening Logic
- Implement clipboard monitoring when the app is running

- Add deduplication to avoid repeated copy-pastes of the same thing

- Timestamp each entry and store in some sort of local database

### Categorization Logic
- Figure out ways of categorizing copy-pastes

Split into:
- URLs
- Code (brackets, semicolons, indentation)
- LaTeX or math equations
- Quotes (common structure, length)
- Plain text / Miscellaneous
- Some sort of other classifier?

### Searching and Indexing
- Implement keyword-based search
- Implement tag-based filtering
- Add fuzzy searching
- Rank results by recency or relevance

### Front End
- Design wireframe (search bar, category filters, list of entries)
- Minimal UI with entries, search, tag filter, etc.
