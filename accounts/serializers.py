# yourapp/serializers.py
from rest_framework import serializers
import random
import hashlib
from rest_framework.response import Response
from rest_framework import status
#Private imports


class LoginSerializer(serializers.Serializer):
    """
    Serializer for handling user login credentials and captcha validation.

    Attributes:
        userloginname (CharField): A field for the user's login name.
        password (CharField): A field for the user's password.
        icompanyid (CharField): A field for the company ID associated with the user.
        db_encode (CharField): A field for encoding related to the database.
        captcha (CharField, write_only): A field for capturing the captcha input provided by the user.
        captcha_hash (CharField, write_only): A field for capturing the hashed value of the captcha answer.

    Methods:
        validate(data): Custom validation method to verify the captcha input against its hashed value.
        verify_captcha(captcha, captcha_hash): Helper method to verify the correctness of the captcha.
        create_captcha(): Static method to generate a random arithmetic captcha question and its hashed answer.
    """
    userloginname = serializers.CharField()
    password = serializers.CharField()
    icompanyid = serializers.CharField()
    db_encode = serializers.CharField()

    captcha = serializers.CharField(write_only=True)
    captcha_hash = serializers.CharField(write_only=True)

    '''
    def validate(self, data):
        """
        Custom validation method to verify the captcha input against its hashed value.

        Args:
            data (dict): The input data containing captcha and captcha hash.

        Returns:
            dict: The validated data if captcha validation passes.

        Raises:
            serializers.ValidationError: If the provided captcha input is invalid.
        """
        captcha = data.get('captcha')
        captcha_hash = data.get('captcha_hash')

        if not self.verify_captcha(captcha, captcha_hash):
            # return Response({'message': 'Invalid CAPTCHA', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            raise serializers.ValidationError("Invalid CAPTCHA")

        return data
    '''

    def verify_captcha(self, captcha, captcha_hash): #-> bool
        """
        Helper method to verify the correctness of the captcha.

        Args:
            captcha (str): The user-provided captcha input.
            captcha_hash (str): The hashed value of the correct captcha answer.

        Returns:
            bool: True if the captcha input matches the hashed answer, False otherwise.
        """
        hashed_captcha = hashlib.sha256(captcha.encode()).hexdigest()
        return hashed_captcha == captcha_hash

    @staticmethod
    def create_captcha():
        """
        Static method to generate a random arithmetic captcha question and its hashed answer.

        Returns:
            tuple: A tuple containing the arithmetic captcha question and its hashed answer.
        """
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        operation = random.choice(['+', '-'])

        if operation == '+':
            captcha_question = f"{num1} + {num2}"
            captcha_answer = str(num1 + num2)
        else:
            if num1 < num2:
                num1, num2 = num2, num1
            captcha_question = f"{num1} - {num2}"
            captcha_answer = str(num1 - num2)

        captcha_hash = hashlib.sha256(captcha_answer.encode()).hexdigest()
        return captcha_question, captcha_hash

    # username = request.data.get('username')
    # password = request.data.get('password')
    # IcompanyID = request.data.get('IcompanyID')
    # db_encode = request.data.get('db_encode')

