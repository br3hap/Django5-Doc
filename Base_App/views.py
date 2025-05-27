from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as AuthLoginView
from Base_App.models import *
from django.contrib.auth import logout
from django.urls import reverse_lazy

# Create your views here.

def HomeView(request):
    items = Items.objects.all()
    list = ItemList.objects.all()
    review = Feedback.objects.all().order_by('-id')[:5]
    return render(request, 'home.html', {'items': items, 'list': list, 'review': review})


def AboutView(request):
    data = AboutUs.objects.all()
    return render(request, 'about.html', {'data': data})


def MenuView(request):
    items = Items.objects.all()
    list = ItemList.objects.all()
    return render(request, 'menu.html', {'items': items, 'list':list})


def bookTableView(request):
    pass

def FeedbackView(request):
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('User_name')
        feedback = request.POST.get('Description')  # Assuming 'Feedback' field is a description
        rating = request.POST.get('Rating')
        image = request.FILES.get('Selfie')  # 'Selfie' field from the form

        # Print to check the values
        print('-->', name, feedback, rating, image)

        # Check if the name is provided
        if name != '':
            # Save the feedback data to the Feedback model
            feedback_data = Feedback(
                User_name=name,
                Description=feedback,
                Rating=rating,
                Image=image  # Save the uploaded image
            )
            feedback_data.save()

            # Add success message
            messages.success(request, 'Feedback submitted successfully!')

            # Optionally, you can redirect or return a success message
            return render(request, 'feedback.html', {'success': 'Feedback submitted successfully!'})

    return render(request, 'feedback.html')