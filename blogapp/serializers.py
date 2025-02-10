from rest_framework import serializers # has default create and update method in rest_framework 
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User #DB model
        fields = ['id','username','password'] #the fields i want to show in the API
        extra_kwargs = {
            'password':{'write_only':True}
            } # this dictionery is used so that password field shou on be write ony,this means when it serialize the data back to JSON , the password will not be included
        
    def create(self, validated_data):# this method is inheritaed from serializers.ModelSerializer, to create new user 
        #create new user and hash the password
            user = User(username = validated_data['username']) #from model User which has been inheritaed
            user.set_password(validated_data['password']) # password  hash gareko through parameter using validated_data
            user.is_active=True # Ensure the user is active
            user.save()
            return user


    

class PostSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField( 
    #this category_id fieLd is defined as primarykeyrelatedfield, which allows us to represent a retionshiip to another model(Category model)
        queryset= Category.objects.all(), #This specifies that the valid options for this field are all instances of the Category model. It ensures that only existing categories can be assigned to a post.
        source = 'category'
        #This indicates that the category_id field will be populated from the category field of the Post model. This means that when i serialize a Post instance, the category_id will correspond to the category relationship.
    )
    category=serializers.StringRelatedField() #it shows the category name instead of id
    author=serializers.StringRelatedField() # it shows the author name instead of object id 
    class Meta():
        model = Post
        fields =[ 
                 'id', # the PK of the post
                 'title', 
                 'author', #this will show the authors username instead of id number
                #  'author_id', # this field is not in DB/model,(The ID of related author, using PrimaryKeyRelatedField)
                 'content', 
                 'created_at',# Time when the post was created
                 'updated_at', # Time when post was updated
                 'category',
                 'category_id' #The ID of the related category (using the PrimaryKeyRelatedField).
            
                ]
        
        
        def create(self, validated_data): #this method is called when creating a new post
            #get the current logged-in user 
            user=self.context['request'].user # Access the request context to get the user, and to associate the new post with user who created it
            validated_data['author']= user # associate the post with the user/author who created it
            # adding the 'author' field to validated data and setting it to the logged-in user, This means that when author save the post, it will be linked to the correct author.
            

class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.PrimaryKeyRelatedField(
        queryset= Post.objects.all(),
        source = 'post'
    )
    post = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    # commented_by = serializers.SerializerMethodField() #Custom field for formatted output
    class Meta():
        model = Comments
        fields = [
            'id',
            'post_id',
            'post',
            'author',
            'comment_content', 
            # 'commented_by', # This field is not in the model, but  adding it to the serializer to display the user who commented
            'commented_at'
            
            ]
    def create(self, validated_data):
        #getting current logged-in user
        logged_in_user = self.context['request'].user # This line retrieves the user who is currently logged in. The self.context contains the request data, and request.user gives us the user object.
        validated_data['author']= logged_in_user # adding the logged-in user as the author of the comment ( This means that when we create the comment, it will be associated with this user.)
        new_comment = super().create(validated_data)  # call parent's class(i.e CommentSeriazer) create method to save comment
        return new_comment # return the newly created comment object
        
    
    # def get_commented_by(self , obj):
    #     return obj.author.username #return the username of the user who commented on the post
             

class CategorySerializer(serializers.ModelSerializer): #this class is for what types of posts are there/ mistakly category  name rakhdeko xu instead of POst/Tags
    class Meta():
        model = Category
        fields = ['id', 'category_name'] #This is a list of fields that should be included in the serialized output
    
    
    def update(self, instance, validated_data):
        instance.category_name = validated_data.get("category_name", instance.category_name) #This line updates the category_name of the instance (the existing Category object) with the new value provided in validated_data.
        #above code - if category_name is not present in validated_data, it retains the current value of instance.category_name.
        total_number = self.Meta.model.objects.filter(category_name = validated_data.get('category_name')).count()
        category_id = validated_data.get('id')
        if category_id: # if category_id exists/provided
            
            try:
                category = self.Meta.model.objects.get(id=category_id)#retrieve the existing category
                category.category_name = validated_data.get('category_name') #update the category name with new value
                category.save() #save the updated category
                return category  # return the updated category
            except self.Meta.model.DoesNotExist:
                raise serializers.ValidationError(
                    "This tags or category not found"
                )
        if total_number > 0:
            raise serializers.ValidationError("This Post/Category/Tags name already exists.")
        instance.save()
        return instance
        
