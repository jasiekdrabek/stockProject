from rest_framework import serializers
from stockApp.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'name', 'surname', 'money', 'role','email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            name=validated_data['name'],
            surname=validated_data['surname'],
            money=validated_data['money'],
            role=validated_data['role'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user