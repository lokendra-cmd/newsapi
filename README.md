# News Summarizer API

A Django-based API that accepts a URL of a news website as input, summarizes the news content on that page, and returns the summary as a JSON response.

## Features

- Accepts a URL of any news website as input
- Extracts the main content from the webpage
- Uses AI-powered summarization to generate a concise summary
- Returns the summary as a JSON response

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd newsapi
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   # On Windows
   .\env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

### API Endpoints

- `POST /api/summarize/`: Accepts a URL and returns a summary of the news content

### Example Request

```bash
curl -X POST http://localhost:8000/api/summarize/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/news-article"}'
```

### Example Response

```json
{
  "url": "https://example.com/news-article",
  "summary": "This is a summary of the news article...",
  "status": "success"
}
```

## Technologies Used

- Django: Web framework
- Django REST Framework: API toolkit
- BeautifulSoup4: HTML parsing
- Transformers: AI-powered text summarization
- PyTorch: Deep learning framework

## License

MIT 