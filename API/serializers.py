from rest_framework import serializers
from Core.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['RFID', 'First_Name', 'Last_Name', 'Email', 'Phone_Number', 'Document_Status']
