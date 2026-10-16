"""Streamlit app that recommends books from several sources.

Secrets are read from `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`).
Run with: streamlit run Book_Recommender.py
"""

import requests
import streamlit as st
from openai import OpenAI

# API configuration
OPENAI_MODEL = "gpt-4o-mini"
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
GUTENBERG_URL = "https://gutendex.com/books/"
NYT_BOOKS_URL = "https://api.nytimes.com/svc/books/v3/lists/current/{list_name}.json"
REQUEST_TIMEOUT = 10  # seconds

openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])
nyt_api_key = st.secrets.get("nyt", {}).get("api_key")


def get_book_recommendations(genre, level, keywords):
    """Ask the OpenAI model for a short, reasoned list of books."""
    user_prompt = f"""
    Recommend books for a {genre} book suitable for {level} learners. The title or preface should contain the following keywords:
    {keywords}.
    For each book, give the title, why it is recommended, at least 3 pros and at least 2 cons.
    """
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=1500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while processing: {e}"


def search_open_library(genre, keywords):
    """Return up to five matches from Open Library, or an error string."""
    try:
        query = f"{genre} {keywords}"
        response = requests.get(
            OPEN_LIBRARY_URL,
            params={"q": query, "limit": 5},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        books = []
        for doc in response.json().get("docs", []):
            key = doc.get("key", "")
            books.append({
                "title": doc.get("title", "No title available"),
                "author": (doc.get("author_name") or ["Unknown Author"])[0],
                "url": f"https://openlibrary.org{key}" if key else "",
            })
        return books
    except Exception as e:
        return f"An error occurred while searching Open Library: {e}"


def search_google_books(genre, keywords):
    """Return up to five matches from Google Books, or an error string."""
    try:
        query = f"{genre} {keywords}"
        response = requests.get(
            GOOGLE_BOOKS_URL,
            params={"q": query, "maxResults": 5},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        books = []
        for item in response.json().get("items", []):
            info = item.get("volumeInfo", {})
            books.append({
                "title": info.get("title", "No title available"),
                "author": ", ".join(info.get("authors", ["Unknown Author"])),
                "url": info.get("infoLink", ""),
            })
        return books
    except Exception as e:
        return f"An error occurred while searching Google Books: {e}"


def search_gutenberg(genre, keywords):
    """Return up to five free public-domain ebooks from Project Gutenberg, or an error string."""
    try:
        query = f"{genre} {keywords}"
        response = requests.get(GUTENBERG_URL, params={"search": query}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        books = []
        for book in response.json().get("results", [])[:5]:
            authors = [a.get("name", "") for a in book.get("authors", [])]
            books.append({
                "title": book.get("title", "No title available"),
                "author": ", ".join(a for a in authors if a) or "Unknown Author",
                "url": f"https://www.gutenberg.org/ebooks/{book.get('id')}",
            })
        return books
    except Exception as e:
        return f"An error occurred while searching Project Gutenberg: {e}"


def search_nyt_bestsellers():
    """Return current NYT hardcover fiction bestsellers, or an error string.

    Needs an NYT Books API key in `[nyt] api_key` in the Streamlit secrets.
    """
    if not nyt_api_key:
        return "NYT Bestsellers is disabled: no NYT API key in secrets."
    try:
        response = requests.get(
            NYT_BOOKS_URL.format(list_name="hardcover-fiction"),
            params={"api-key": nyt_api_key},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        books = []
        for book in response.json().get("results", {}).get("books", [])[:5]:
            books.append({
                "title": book.get("title", "No title available").title(),
                "author": book.get("author", "Unknown Author"),
                "url": book.get("amazon_product_url", ""),
            })
        return books
    except Exception as e:
        return f"An error occurred while searching NYT Bestsellers: {e}"


st.title("Book Recommender")

book_genre = st.text_input("Enter the book genre (e.g., Data Science, Fiction, etc.)")
book_level = st.selectbox("Select the level", ["Beginner", "Intermediate", "Advanced"])
keywords = st.text_area("Enter keywords (separate by commas)")

if st.button("Get Book Recommendations"):
    if not book_genre or not keywords:
        st.error("Please fill in the genre and keywords.")
    else:
        st.subheader("Recommended books by OpenAI")
        st.write(get_book_recommendations(book_genre, book_level, keywords))

        sources = [
            ("Open Library", search_open_library(book_genre, keywords)),
            ("Google Books", search_google_books(book_genre, keywords)),
            ("Project Gutenberg", search_gutenberg(book_genre, keywords)),
            ("NYT Bestsellers", search_nyt_bestsellers()),
        ]

        for source_name, result in sources:
            st.subheader(f"Books from {source_name}")
            if isinstance(result, str):
                st.warning(result)
            elif not result:
                st.info(f"No books found on {source_name}.")
            else:
                for idx, book in enumerate(result, 1):
                    st.write(f"{idx}. **{book['title']}** by {book['author']}")
                    if book["url"]:
                        st.write(f"More details: {book['url']}")
