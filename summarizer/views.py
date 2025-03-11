from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import URLSerializer
import requests
from bs4 import BeautifulSoup
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Initialize variables
MODEL_NAME = "sshleifer/distilbart-cnn-6-6"
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        try:
            # Import torch and transformers here to handle potential import errors
            import torch
            from transformers import pipeline
            
            # Always use CPU for Railway deployment
            device = -1
            
            logger.info(f"Initializing summarization model {MODEL_NAME} on CPU")
            summarizer = pipeline(
                "summarization", 
                model=MODEL_NAME, 
                device=device
            )
            return summarizer
        except Exception as e:
            logger.error(f"Error initializing summarizer: {str(e)}")
            # Return a simple fallback summarizer if the model fails to load
            return FallbackSummarizer()
    return summarizer

class FallbackSummarizer:
    """A simple fallback summarizer that returns the first few sentences if the model fails to load"""
    def __call__(self, text, **kwargs):
        # Simple extractive summary - first 3 sentences or 100 characters
        sentences = text.split('.')
        summary = '. '.join(sentences[:3]) + '.'
        if len(summary) > 100:
            summary = summary[:100] + '...'
        return [{'summary_text': f"[BASIC SUMMARY] {summary}"}]

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
                try:
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
                except Exception as e:
                    logger.error(f"Error generating summary: {str(e)}")
                    # Return a basic summary if the model fails
                    return Response({
                        'url': url,
                        'summary': f"Could not generate AI summary due to an error. Here's the beginning of the article: {text[:150]}...",
                        'status': 'partial_success'
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
