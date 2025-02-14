from rest_framework import serializers # has default create and update method in rest_framework 
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta: #The Meta class is a nested class that provides metadata to the serializer
        model = User #DB model imported
        fields = ['id','username','password'] #the fields i want to show in the API
        extra_kwargs = { #extra keyword arguments . purpose: The extra_kwargs dictionary allows us to specify additional options for specific fields.
            'password':{'write_only':True}
            } 
        
        """password:{'write_only':True} = this dictionery is used so that password field should on be write only,this means 
       when it serialize the data back to JSON , the password will not be included in output.
       important for security reasons, as users typically do not want to expose user passwords in API responses. """
    
    def create(self, validated_data):# this method is inheritaed from serializers.ModelSerializer, to create new user 
    
        """ This method overrides the default create method provided by ModelSerializer. 
        It is responsible for creating a new user instance. By overriding this method, we can customize the user 
        creation process, such as hashing the password before saving it to the database."""
    
        user = User(username = validated_data['username']) #from model User which has been inheritaed
        """validated_data['username']---It retrieves the username that the user provided when creating a new account. 
        This value is expected to be present in the input data that was validated by the serializer."""
        
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
            #validated_data: This parameter is a dictionary that contains the data that has been validated by the serializer. It includes all the fields that are required to create a new Post instance,
            #get the current logged-in user 
            user=self.context['request'].user # Access the request context to get the currently logged in user, and to associate the new post with user who created it
            validated_data['author']= user # associate the post with the user/author who created it, purpose =  This line adds the current user to the validated_data dictionary under the key 'author'.
            # adding the 'author' field to validated data and setting it to the logged-in user, This means that when author save the post, it will be linked to the correct author.
            """When creating a new post, we want to associate it with the user who is currently logged in. 
            By adding the user to validated_data, we ensure that when the post is saved, 
            the author field of the Post model will be populated with the correct user."""

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
        """In simpler terms, it checks if the user has given a new name for the category. 
        If they have, it updates the category name to that new name. If they haven't, it keeps the old name.
        
        Let's say i have a category with the name "Technology" and i want to update it:
        If validated_data contains {"category_name": "Tech"}, then:
        instance.category_name will be updated to "Tech".
        If validated_data contains {}, meaning no new category name is provided, then:
        instance.category_name will remain "Technology"."""
        
        total_number = self.Meta.model.objects.filter(category_name = validated_data.get('category_name')).count() #This variable counts how many categories have the same name as the one provided in validated_data.
        category_id = validated_data.get('id') #This retrieves the ID of the category being updated from validated_data.

        if category_id: # if category_id exists/provided, If it is, it attempts to retrieve the existing category from the database.
            
            try:
                category = self.Meta.model.objects.get(id=category_id)#retrieve the existing category
                category.category_name = validated_data.get('category_name') #update the category name with new value
                category.save() #save the updated category
                return category  # return the updated category
            except self.Meta.model.DoesNotExist:
                #If the category does not exist, it raises a ValidationError with a message indicating that the category was not found.
                raise serializers.ValidationError(
                    "This tags or category not found"
                )
        
        #This line checks if there are any existing categories with the same name as the one being updated.
        if total_number > 0: # indicating that if the category name already exists in the database. This prevents duplicate category names.
            raise serializers.ValidationError("This Post/Category/Tags name already exists.")
        instance.save()
        return instance
        
