from django.urls import path
from .views import SummarizeNewsView

urlpatterns = [
    path('summarize/', SummarizeNewsView.as_view(), name='summarize_news'),
] 