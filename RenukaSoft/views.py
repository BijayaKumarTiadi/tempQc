from django.http import HttpResponse,JsonResponse
from django.shortcuts import render

def home_page(request):
    friends=['API Server Running ...']
    return JsonResponse(friends,safe=False)