# Book Recommender

A Streamlit app that recommends books for a topic and reading level. It combines an AI-written shortlist from OpenAI with live search results from Open Library, Google Books and Project Gutenberg, and optionally the NYT Bestsellers list.

## Features

1. **AI recommendations.** An OpenAI model suggests books for your genre and level, with a reason, pros and cons for each.
2. **Live search.** Results from:
   - **Open Library**: catalogue search, with links to each work
   - **Google Books**: titles, authors and info links
   - **Project Gutenberg**: free public-domain ebooks, with download pages
   - **NYT Bestsellers** (optional): current hardcover fiction list, if you add an API key

Each source shows up to five results. A source that fails shows its error message rather than failing the whole page.

## Setup

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy the secrets template and add your keys:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   - `[openai] api_key` is required.
   - `[nyt] api_key` is optional. Without it, the NYT source is skipped.

   Never commit `.streamlit/secrets.toml`. It is listed in `.gitignore`.

3. Run the app:

   ```bash
   streamlit run Book_Recommender.py
   ```

## Usage

1. Enter a **genre** (for example, "Data Science" or "Historical Fiction").
2. Choose a **level**: Beginner, Intermediate or Advanced.
3. Enter **keywords** separated by commas, for example "machine learning, Python".
4. Click **Get Book Recommendations**.

## Configuration

| Setting | Where | Default |
|---|---|---|
| OpenAI model | `OPENAI_MODEL` in `Book_Recommender.py` | `gpt-4o-mini` |
| Results per source | `[:5]` slices and `maxResults` / `limit` in the search functions | 5 |
| HTTP timeout | `REQUEST_TIMEOUT` | 10 seconds |

## Notes and limitations

- AI recommendations are generated, not looked up. Check that a suggested title exists before buying it.
- Search quality depends on the source. Broad genres with many keywords can return few results; try fewer, more specific keywords.
- The app has no automated tests yet. Test changes by running the app with a valid OpenAI key.

## Project structure

| File | Purpose |
|---|---|
| `Book_Recommender.py` | The Streamlit app and all source integrations |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml.example` | Template for API keys |
| `.gitignore` | Keeps secrets and caches out of git |
