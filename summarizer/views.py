from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import URLSerializer
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class SummarizeNewsView(APIView):
    """
    API view to summarize news articles from a given URL.
    """
    def post(self, request, format=None):
        serializer = URLSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            try:
                # Fetch the content of the URL
                response = requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text from paragraphs (typical for news articles)
                paragraphs = soup.find_all('p')
                text = ' '.join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
                
                # If text is too long, truncate it to avoid model limitations
                max_input_length = 1024  # Adjust based on model requirements
                if len(text) > max_input_length:
                    text = text[:max_input_length]
                
                # Initialize the summarization pipeline
                summarizer = pipeline("summarization")
                
                # Generate summary
                summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
                
                # Return the summary as JSON
                return Response({
                    'url': url,
                    'summary': summary[0]['summary_text'],
                    'status': 'success'
                }, status=status.HTTP_200_OK)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching URL {url}: {str(e)}")
                return Response({
                    'error': f"Error fetching URL: {str(e)}",
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                return Response({
                    'error': f"Error processing URL: {str(e)}",
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
