from django_filters import rest_framework as filters
from .models import *

class PostFilter(filters.FilterSet):
    author = filters.CharFilter(field_name= 'author__username', lookup_expr='icontains') #Filters posts by the author's username, using a case-insensitive match.
    title = filters.CharFilter(field_name='title', lookup_expr='icontains') #Filters posts by title, also case-insensitive.
    created_at = filters.DateFilter(field_name='created_at') # Allows filtering by the creation date of the post
    category = filters.CharFilter(field_name='category__category_name', lookup_expr='icontains')#Filters posts by category name, case-insensitive.
    
    class Meta:
        model = Post
        fields = {
            
            'category',
            'author',
            'title',
            'created_at'
                
            }