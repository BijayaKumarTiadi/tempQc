from django.http import HttpResponse,JsonResponse

def home_page(request):
    friends=['API Server Running ...']
    return JsonResponse(friends,safe=False)