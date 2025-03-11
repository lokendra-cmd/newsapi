# News Summarizer API

A Django-based API that accepts a URL of a news website as input, summarizes the news content on that page, and returns the summary as a JSON response.

## Features

- Accepts a URL of any news website as input
- Extracts the main content from the webpage
- Uses AI-powered summarization to generate a concise summary
- Returns the summary as a JSON response
- Optimized for Railway deployment

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

## Deployment to Railway

### Option 1: Deploy via GitHub

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. Connect to Railway:
   - Create a Railway account at [railway.app](https://railway.app/)
   - Create a new project
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect your Django project

3. Set Environment Variables:
   - In the Railway dashboard, go to your project
   - Click on the "Variables" tab
   - Add the following environment variables:
     - `SECRET_KEY`: A secure random string
     - `DEBUG`: Set to "False"

4. Your API will be available at the URL provided by Railway

### Option 2: Deploy via Railway CLI

1. Install the Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link to your project:
   ```bash
   railway link
   ```

4. Deploy your project:
   ```bash
   railway up
   ```

## Performance Considerations

- The API uses a smaller, more efficient model (`sshleifer/distilbart-cnn-6-6`) to ensure compatibility with Railway's resource constraints
- The first request may take longer as the model is loaded into memory
- Subsequent requests will be faster as the model remains in memory

## Technologies Used

- Django: Web framework
- Django REST Framework: API toolkit
- BeautifulSoup4: HTML parsing
- Transformers: AI-powered text summarization
- PyTorch: Deep learning framework
- Railway: Deployment platform

## License

MIT 