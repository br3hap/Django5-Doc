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

def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Items, id=item_id)

        cart = request.session.get('cart', {})

        if item_id in cart:
            cart[item_id]['quantity'] += 1
        else:
            cart[item_id] = {
                'name': item.Item_name,
                'price':item.Price,
                'quantity':1
            }
        
        request.session['cart'] = cart

        return JsonResponse({'message': 'Item added to cart', 'cart': cart})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

def get_cart_items(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user = request.user).select_related('item')
        items = [
            {
                'name': cart_item.item.Item_name,
                'quantity': cart_item.quantity,
                'price': cart_item.item.Price,
                'total': cart_item.quantity * cart_item.item.Price
            }
            for cart_item in cart_items
        ]
        return JsonResponse({'items': items}, safe=False)
    return JsonResponse({'error': 'User not authenticated'}, status=401)


class LoginView(AuthLoginView):
    template_name = 'login.html'
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('Home')
    

def LogoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('Home')


def SignupView(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('Home')
        else:
            messages.error(request, 'Error during signup. Please try again')
    else:
        form = UserCreationForm()
    return render(request, 'login.html', {'form': form, 'tab': 'signup'})
    

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
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY

    if request.method == 'POST':
        name = request.POST.get('user_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('user_email')
        total_person = request.POST.get('total_person')
        booking_data = request.POST.get('booking_data')

        if name != '' and len(phone_number) == 10 and email != '' and total_person != '0' and booking_data != '':
            data = BookTable(Name=name, Phone_number=phone_number,
                             Email=email, Total_person=total_person,
                             Booking_date=booking_data)
            data.save()

            subject = 'Booking Confirmation'
            message =   f"Hello {name},\n\nYour booking has been successfully received.\n" \
                        f"Booking details:\nTotal persons: {total_person}\n" \
                        f"Booking date: {booking_data}\n\nThank you for choosing us!"
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            messages.success(request, 'Booking request submitted successfully! Please check your confirmation email.')

            return render(request, 'feedback.html', {'success': 'Booking request submitted successfully! Please check your confirmation email.'})
        
    return render(request, 'book_table.html', {'google_maps_api_key': google_maps_api_key})




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