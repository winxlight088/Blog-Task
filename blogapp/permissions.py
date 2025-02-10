from rest_framework.permissions import IsAuthenticatedOrReadOnly #this is the name of custom permissions class
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS #SAFE_METHOD contains HTTP methods like GET, HEAD,...options

class IsAuthenticatedOrReadOnly(BasePermission): # this class allows read only access to unauthenticated users, if authenticated then users are able to CRUD
    def has_permission(self, request, view): #this method/function check if a user has permission to access a view like (API)
        
        
        return request.method in SAFE_METHODS or (request.user and request.user.is_authenticated)
    
    
        #purpose:first checks if the request is for safe method like "get", if itrue then grant access,
        #if the request is not safe method (like post, put or delete), and also if the user is logged in (request.user.is_authenticated)
        #if the user is logged in,it allows access, if not it denies....
class IsCommentAuthor(BasePermission):
    """
    Custom permission to only allow authors of a commentors to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        
        return obj.author == request.user
