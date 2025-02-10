from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from .permissions import IsAuthenticatedOrReadOnly, IsCommentAuthor
from rest_framework.authtoken.models import Token
from .models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserViewSet(viewsets.ModelViewSet): #inheriting viewsets.modelViewset which is built-in functionality for handling HTTP methods
    #----attributes-------
    queryset = User.objects.all() #retrieve the instance/objects of User Model from DB. 
    #Purpose: When a request is made to this viewset, the queryset will determine which user instances/objects are available for retrieval, updating, or deletion.
    
    serializer_class = UserSerializer 
    # Serializer Class: This line specifies the serializer class that will be used to convert "User" instances to and from JSON (or other content types).
   #imported from permissions.py fiLE
    
   

class LoginAPIView(APIView): # LoginAPIView is used to handle user login request,  aowing users to authenticate by providing their username and password  
     @swagger_auto_schema( #decorator to add swagger documentation for post method using drf_yasg library
         request_body= openapi.Schema(
                 type = openapi.TYPE_OBJECT,properties={ #Indicates that the request body should be a JSON object.
                     "username":openapi.Schema(title = "password",type = openapi.TYPE_STRING,), #a string representing the user's username.
                     "password":openapi.Schema(title = "password",type = openapi.TYPE_STRING,), #a string representing the user's password.
                 },
            required = ["username","password"],
            #required: Specifies that both username and password fields are required in the request body when logging in.
         )
    )
     def post(self,request): #post method, which will handle POST requests to the login. containing parameter ''request''
        user_input_username = request.data.get('username') # extracting the username and password from the request data
        user_input_password = request.data.get('password')
        if user_input_username == "" and user_input_password == "" :#if username and password both are empty then 
            return Response({
                "Response": "Username and Password fields are empty"
            },status=404) # If both fields are empty, it returns a 404 response with a message indicating that the fields are empty.
       
        #if the user is sucessfully registered from (UserViewSet-UserSerializer) then Django's built-in authenticate function to check if the provided username and password match a registered user.
        authenticated_user = authenticate(username= user_input_username, password = user_input_password) #to authenticate if both registered username and password is correct
        #the left side ('username') refers to parameter name expected by the authenticate function
        if authenticated_user : # if there is authenticated user = True
           token,_ = Token.objects.get_or_create(user = authenticated_user) 
           #If the user is authenticated, it retrieves or creates an authentication token for the user using Django REST Framework's token authentication.
           
           return Response({
               "token":token.key, #display authentication token for user
               "user": user_input_username, #display the logged in username
               "success":"User logged in" #message
           })
        else: #if fail to authenticate
            return Response({
                "Response":"Invalid username or password"
            },status=401)# return unauthorized response
        
#<-----------------------------------------------------------------------------------------------------------------------------------------------------------
# class UserRegisterView(CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class UserLoginView(GenericAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     def post(self, request):
#         username = request.data.get('username') # get username from request
#         password = request.data.get('password')
#         if username == "" and password =="":
#             return Response ({
#                 "Response": "Both fields are empty"
#             })
#         elif username == "" or password == "":
#             return Response({
#                 "Response":"One of the field is empty"
#             })
#         #authenticate user with provided credentials
#         user_auth = authenticate(username = username, password = password) 
#<_-------------------------------------------------------------------------------------------------------------------------------------------------


class PostViewSet(viewsets.ModelViewSet): #for posting 
    queryset=Post.objects.all() #retrieves all instances of the Post model. This queryset will be used for operations like listing all posts or retrieving a specific post.
    serializer_class = PostSerializer
    # Serializer Class: This line specifies the serializer class  will be used to convert "Post" instances to JSON or from JSON (or other content types).

    permission_classes = [IsAuthenticatedOrReadOnly] # FROM permissions.py imported ---
    
    """The IsAuthenticatedOrReadOnly permission class allows authenticated users to perform any action (create, update, delete),---
    if unauthenticated users, then can only read (GET) posts. This ensures that only logged-in users can create or modify posts"""
    
    def perform_create(self, serializer):
        #rest-framework built in function to perform create operation. this function/method is called when a POST request is made to  create new post.
        #This method allows for custom behavior during the creation of a new post.
        
        serializer.save(author=self.request.user) ##Saving the post with the logged-in user as the author( Automatically set the author to the logged-in user)
        # calls the save method on the serializer, which saves the new post instance to the database

#------------------------------------------------------------------------------------------------------------------
    # def get(self, request):
    #     post_get = Post.objects.all()
    #     serializer = PostSerializer(post_get, many=True)
    #     return Response(serializer.data)
    
    # def post(self, request): # this method is to create a new post
    #     serializer = PostSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True) #is_valid checks if the data send by user is valid or not
    #     serializer.save()
    #     return Response({
    #         "Response": "Post created"
    #     })
#------------------------------------------------------------------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all() #retrieves all instances of the Category model. This queryset will be used for operations like listing all available tags/category or retrieving a specific tags/category.
    serializer_class = CategorySerializer # convert "Category" instances to JSON or from JSON to objects
    permission_classes=[IsAuthenticatedOrReadOnly]

class CommentViewSet(viewsets.ModelViewSet):
    queryset= Comments.objects.all()
    serializer_class = CommentSerializer # convert "Comment" instances to JSON or from JSON to objects
    
    permission_classes=[IsAuthenticatedOrReadOnly, IsCommentAuthor] #if proper authenticated(logged in) users then allow CRUD operations else only read operation is allowed.
    #IsCommentAuthor permission class checks if the user trying to update or delete a comment is the author of that comment. This ensures that only the user who created the comment can modify or delete it.
    def perform_create(self, serializer): #this function/method is called when a POST request is made to  create new comment.
        
        if self.request.user.is_authenticated: # checks if the user making request is logged-in (authenticated)
            return serializer.save(author=self.request.user) 
            """The author field is automatically set to the currently logged-in user (self.request.user),--
            making sure that the comment is related with the user who commented on the post.
            If the reuqested user is authenticated, it calls the save method on the serializer, which saves the new comment instance to the database"""
        else:
            raise serializers.ValidationError()
            #if the user is not authenticated,  raises a ValidationError
  
# class CommentDetailViewSet(viewsets.ModelViewSet):
#     queryset = Comments.objects.all()
#     serializer_class = CommentSerializer
#     permission_classes =[IsCommentAuthor, IsAuthenticatedOrReadOnly]

   