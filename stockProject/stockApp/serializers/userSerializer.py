from rest_framework import serializers
from stockApp.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'name', 'surname','email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validatedData):
        user = CustomUser(
            username=validatedData['username'],
            name=validatedData['name'],
            surname=validatedData['surname'],
            money=10000.0,
            moneyAfterTransations=10000.0,
            role='ROLE_USER',
            email=validatedData['email']
        )
        user.set_password(validatedData['password'])
        user.save()
        return user