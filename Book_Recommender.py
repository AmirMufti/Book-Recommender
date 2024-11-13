#!/usr/bin/env python
# coding: utf-8

# In[2]:


import openai
import os
import requests
import streamlit as st

# API Key setup for OpenAI
openai_api_key = st.secrets["openai"]["api_key"]
openai.api_key = openai_api_key
MODEL = 'gpt-4'

# API URLs for various book sources
OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
ISBNDB_URL = "https://api.isbndb.com/books/{isbn}"
GUTENBERG_URL = "https://gutendex.com/api/v2/works"
NYT_BOOKS_URL = "https://api.nytimes.com/svc/books/v3/lists/current/{list-name}.json"
LIBRARYTHING_URL = "https://www.librarything.com/services/rest/1.1"
PDFDRIVE_URL = "https://www.pdfdrive.com/search?q="

# Streamlit application
st.title("Book Recommender")

# User inputs for book genre, level, and keywords
book_genre = st.text_input("Enter the book genre (e.g., Data Science, Fiction, etc.)")
book_level = st.selectbox("Select the level", ["Beginner", "Intermediate", "Advanced"])
keywords = st.text_area("Enter keywords (separate by commas)")

# Function to query OpenAI API and get book recommendations
def get_book_recommendations(genre, level, keywords):
    # Constructing the prompt for OpenAI based on user input
    user_prompt = f"""
    Recommend books for a {genre} book suitable for {level} learners. The title or preface should contain the following keywords:
    {keywords}.
    Provide the book title, why it's recommended, pros (at least 3), and cons (at least 2).
    """

    # Handle OpenAI API request
    try:
        # Query OpenAI API to get book recommendations
        response = openai.Completion.create(
            model=MODEL,  # Use the latest available model
            prompt=user_prompt,
            max_tokens=1500,  # Adjust based on your needs
            temperature=0.7,  # Controls randomness in the output
        )
        
        # Extract the recommendation from OpenAI response
        recommended_books = response.choices[0].text.strip()
        return recommended_books

    except Exception as e:
        return f"An error occurred while processing: {e}"

# Function to search books on Open Library based on genre/keywords
def search_open_library(genre, keywords):
    try:
        # Combine genre and keywords to create a search query
        query = f"{genre} {keywords}"
        
        # Make a request to Open Library's search API
        response = requests.get(OPEN_LIBRARY_URL, params={"q": query, "limit": 5})
        data = response.json()
        
        # Extract book details
        books = []
        for book in data["docs"]:
            title = book.get("title", "No title available")
            author = book.get("author_name", ["Unknown Author"])[0]
            key = book.get("key", "")
            book_url = f"https://openlibrary.org{key}" if key else ""
            books.append({"title": title, "author": author, "url": book_url})
        
        return books
    except Exception as e:
        return f"An error occurred while searching Open Library: {e}"

# Function to search books on Google Books based on genre/keywords
def search_google_books(genre, keywords):
    try:
        # Combine genre and keywords to create a search query
        query = f"{genre} {keywords}"
        
        # Make a request to Google Books API
        response = requests.get(GOOGLE_BOOKS_URL, params={"q": query, "maxResults": 5})
        data = response.json()
        
        # Extract book details
        books = []
        for book in data.get('items', []):
            title = book.get("volumeInfo", {}).get("title", "No title available")
            authors = book.get("volumeInfo", {}).get("authors", ["Unknown Author"])
            book_url = book.get("volumeInfo", {}).get("infoLink", "")
            books.append({"title": title, "author": ", ".join(authors), "url": book_url})
        
        return books
    except Exception as e:
        return f"An error occurred while searching Google Books: {e}"

# Function to search books on Project Gutenberg based on genre/keywords
def search_gutenberg(genre, keywords):
    try:
        query = f"{genre} {keywords}"
        response = requests.get(GUTENBERG_URL, params={"search": query})
        data = response.json()

        books = []
        for book in data.get("results", []):
            title = book.get("title", "No title available")
            author = book.get("author", "Unknown Author")
            book_url = f"https://www.gutenberg.org/ebooks/{book.get('id')}"
            books.append({"title": title, "author": author, "url": book_url})

        return books
    except Exception as e:
        return f"An error occurred while searching Project Gutenberg: {e}"

# Function to get books from NYT Bestsellers
def search_nyt_bestsellers():
    try:
        response = requests.get(NYT_BOOKS_URL.format(name="hardcover-fiction"), params={"api-key": "YOUR_NYT_API_KEY"})
        data = response.json()
        books = []
        for book in data['results']:
            title = book.get("title", "No title available")
            author = book.get("author", "Unknown Author")
            book_url = book.get("url", "")
            books.append({"title": title, "author": author, "url": book_url})
        return books
    except Exception as e:
        return f"An error occurred while searching NYT Bestsellers: {e}"

# Function to search books on LibraryThing based on genre/keywords
def search_librarything(genre, keywords):
    try:
        query = f"{genre} {keywords}"
        response = requests.get(LIBRARYTHING_URL, params={"q": query})
        data = response.json()
        
        books = []
        for book in data.get("works", []):
            title = book.get("title", "No title available")
            author = book.get("author", "Unknown Author")
            book_url = f"https://www.librarything.com/work/{book.get('key')}"
            books.append({"title": title, "author": author, "url": book_url})

        return books
    except Exception as e:
        return f"An error occurred while searching LibraryThing: {e}"

# Function to search books on PDFDrive based on genre/keywords
def search_pdfdrive(genre, keywords):
    try:
        query = f"{genre} {keywords}"
        response = requests.get(PDFDRIVE_URL + query)
        books = []
        # You would need to extract and parse the book data from the PDFDrive site
        # Example placeholder - Replace with actual parsing logic
        books.append({"title": "Example Book from PDFDrive", "author": "Unknown Author", "url": "URL"})
        
        return books
    except Exception as e:
        return f"An error occurred while searching PDFDrive: {e}"

# Button to trigger book recommendation and search
if st.button("Get Book Recommendations"):
    if not book_genre or not book_level or not keywords:
        st.error("Please fill in all fields!")
    else:
        # Get book recommendations based on user input (OpenAI)
        recommendations = get_book_recommendations(book_genre, book_level, keywords)
        st.subheader("Recommended Books by OpenAI:")
        st.write(recommendations)
        
        # Search for books from various sources
        sources = [
            ("Open Library", search_open_library(book_genre, keywords)),
            ("Google Books", search_google_books(book_genre, keywords)),
            ("Project Gutenberg", search_gutenberg(book_genre, keywords)),
            ("NYT Bestsellers", search_nyt_bestsellers()),
            ("LibraryThing", search_librarything(book_genre, keywords)),
            ("PDFDrive", search_pdfdrive(book_genre, keywords))
        ]
        
        for source_name, books in sources:
            if isinstance(books, list) and books:
                st.subheader(f"Books from {source_name}:")
                for idx, book in enumerate(books, 1):
                    st.write(f"{idx}. {book['title']} by {book['author']}")
                    st.write(f"More details: {book['url']}")
            else:
                st.error(f"No books found from {source_name}.")


# In[ ]:




