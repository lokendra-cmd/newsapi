from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import URLSerializer
import requests
from bs4 import BeautifulSoup
import logging
import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

# Initialize the model globally to avoid reloading it on each request
# Use a smaller, more efficient model
MODEL_NAME = "sshleifer/distilbart-cnn-6-6"
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        # Check if CUDA is available, but default to CPU for Railway
        device = -1  # Use CPU by default for compatibility
        
        # Set lower precision for efficiency
        torch_dtype = torch.float32
        if torch.cuda.is_available():
            device = 0  # Use GPU if available
            torch_dtype = torch.float16  # Use half precision if on GPU
            
        logger.info(f"Initializing summarization model {MODEL_NAME} on device {device}")
        summarizer = pipeline(
            "summarization", 
            model=MODEL_NAME, 
            device=device,
            torch_dtype=torch_dtype
        )
    return summarizer

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
                }, timeout=10)  # Add timeout
                response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text from paragraphs (typical for news articles)
                paragraphs = soup.find_all('p')
                text = ' '.join([para.get_text().strip() for para in paragraphs if para.get_text().strip()])
                
                # If text is too long, truncate it to avoid model limitations
                # Use a smaller input length for efficiency
                max_input_length = 512  # Reduced from 1024
                if len(text) > max_input_length:
                    text = text[:max_input_length]
                
                if not text:
                    return Response({
                        'error': "Could not extract text from the provided URL",
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get the summarizer
                summarizer_instance = get_summarizer()
                
                # Generate summary with optimized parameters
                summary = summarizer_instance(
                    text, 
                    max_length=100,  # Shorter summary
                    min_length=30, 
                    do_sample=False,
                    truncation=True
                )
                
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
