from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import connection, connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from estimation.models import EstItemtypemaster
from estimation.serializers import EstItemtypemasterSerializer
# Create your views here.


class EstimationHome(APIView):
    """
    EstimationHome view accessible only to authenticated users.
    """
    

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
            operation_summary="Estimation App",
            operation_description="Retrieves type of cartonss information for the authenticated user.",
            responses={
                200: "Success",
                401: "Unauthorized",
                500: "Internal server error"
            }
        )
    

    def get(self, request):
        try:
            queryset = EstItemtypemaster.objects.prefetch_related('itemtypedetail_set').all()
            serializer = EstItemtypemasterSerializer(queryset, many=True)
            return Response({"message": "Success","data": serializer.data},status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Failed to fetch Estimation information: {str(e)}"
            return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    


