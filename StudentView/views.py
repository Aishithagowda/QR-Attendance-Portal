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
