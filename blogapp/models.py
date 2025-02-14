from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() #calling get_user_model to get user (DB) model from setting.py fie
# Create your models here.

class Category(models.Model):# what type of post/tags
    category_name = models.CharField(max_length=100, unique= True)
    
    def __str__(self): #this is to return a string representation of the object,__str__ method allows you to specify how instances of the model should be represented as strings, 
        return self.category_name # 

class Post(models.Model): #database for authors
    title = models.CharField(max_length=255) #title of post
    author = models.ForeignKey(User, on_delete=models.CASCADE) #id from predefined django.contrib.auth
    content = models.TextField() # what author want to wirte as a content
    created_at = models.DateTimeField(auto_now_add=True) #auto_now_add field is saved as the current timestamp when a row is first added to the database, and is therefore perfect for tracking when it was created.
    updated_at = models.DateTimeField(auto_now = True) #auto_now fields are updated to the current timestamp every time an object is saved and are therefore perfect for tracking when an object was last modified
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self): # __str__ method is used to define a string representation of an object. 
        return self.title
    
class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) 
    #If three users comment on this post, the Comment entries might look like this:
    # Comment 1: "Great article!" (Post ID: 1)
    # Comment 2: "Very helpful, thanks!" (Post ID: 1)
    # Comment 3: "Looking forward to more tutorials." (Post ID: 1)
    author = models.ForeignKey(User, on_delete=models.CASCADE) #COMMENTERS are able to comment on the authors post
    
    comment_content = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self):
        return f"{self.post}"