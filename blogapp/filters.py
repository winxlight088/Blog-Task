from django_filters import rest_framework as filters
from .models import *

class PostFilter(filters.FilterSet):
    # author = filters.CharFilter(field_name='author__username')
    # title = filters.CharFilter()
    created_at = filters.DateFilter(field_name='created_at')
    # category = filters.CharFilter(field_name='category__category_name')
    
    class Meta:
        model = Post
        fields = {
            'category':['exact'],
            
            
        }