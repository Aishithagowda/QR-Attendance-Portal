from django.shortcuts import render
from django.contrib.auth import authenticate, login
from FacultyView.models import Student
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json

# Create your views here.

present = set()
scanned_devices = set()  # Set to store unique device IDs

def mark_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        device_id = data.get('deviceId')

        if device_id in scanned_devices:
            return JsonResponse({'success': False})

        scanned_devices.add(device_id)
        return JsonResponse({'success': True})

@never_cache
def add_manually_post(request):
    if request.method == "POST":
        usn = request.POST.get("usn")
        password = request.POST.get("password")
        
        user = authenticate(username=usn, password=password)
        
        if user is not None:
            
            login(request, user)
            student = Student.objects.get(user=user)
            present.add(student)
            
            return HttpResponseRedirect(reverse("submitted"))
        else:
            # Authentication failed
            return render(request, "StudentView/StudentViewIndex.html", {"error": "Invalid credentials"})
    else:
        return render(request, "StudentView/StudentViewIndex.html")


def submitted(request):
    return render(request, "StudentView/Submitted.html")
