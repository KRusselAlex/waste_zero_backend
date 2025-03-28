from django.http import HttpResponse

def deployment_status(request):
    return HttpResponse("Backend is deployed and prepared to run")