from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

class UserRegistrationSerializer(BaseUserRegistrationSerializer):

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ['id', 'email', 'password', 'first_name', 'last_name' , 'username']

class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'first_name', 'last_name' , 'username']

