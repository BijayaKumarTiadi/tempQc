from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import TextMatterChecking
from .serializers import TextMatterCheckingSerializer

class TextMatterCheckingViewSet(viewsets.ModelViewSet):
    queryset = TextMatterChecking.objects.all()
    serializer_class = TextMatterCheckingSerializer

    @swagger_auto_schema(
        operation_summary="List all Text Matter Checkings",
        operation_description="Retrieve a list of all text matter checkings",
        responses={200: TextMatterCheckingSerializer(many=True)},
        tags=['Text Matter Checking']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Text Matter Checking",
        operation_description="Retrieve a text matter checking by JobId",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Text Matter Checking",
        operation_description="Create a new text matter checking",
        request_body=TextMatterCheckingSerializer,
        responses={201: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Text Matter Checking",
        operation_description="Update an existing text matter checking",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextMatterCheckingSerializer,
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially Update a Text Matter Checking",
        operation_description="Partially update an existing text matter checking",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextMatterCheckingSerializer,
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Text Matter Checking",
        operation_description="Delete a text matter checking by JobId",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        responses={204: "No Content"},
        tags=['Text Matter Checking']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
