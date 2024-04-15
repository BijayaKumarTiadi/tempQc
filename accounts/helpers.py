__author__ = "Bijaya Kumar , Sailedra Tiwari"
__copyright__ = "Copyright 2024, SmartMIS"
__credits__ = ["Manish", "Mohit", "Sailedra",
                    "Bijaya"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Renuka Softtech"
__email__ = "manish@renukasofttech.com"
__status__ = "Testing"


from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

class GetUserData:

    @staticmethod
    def get_userid(request):
        """
        Returns the user_id of the logged user from the AccessToken provided in the header.
        : Authorization Bearer <token>
        """
        try:
            header = request.headers.get('Authorization')
            parts = header.split()
            access_token = parts[1]
            access_token = AccessToken(access_token)
            user_id = access_token['user_id']
            return user_id
        except Exception as e:
            error_message = f"Failed to fetch user information for user id: {str(e)}"
            return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_user(request):
        """
        Returns the CustomUser object based on the user_id obtained from the access token.
        """
        user_id = GetUserData.get_userid(request)
        try:
            user = get_user_model().objects.get(id=user_id)
            return user
        except get_user_model().DoesNotExist:
            error_message = f"User with ID {user_id} does not exist"
            return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error_message = f"Failed to fetch user information for user id: {str(e)}"
            return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)