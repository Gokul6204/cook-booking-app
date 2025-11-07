from datetime import date as date_class

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserRegisterForm, LoginForm, CookProfileForm, BookingForm, ReviewForm, UserUpdateForm
from .models import User, CookProfile, Booking, Review


def home(request: HttpRequest) -> HttpResponse:
    featured = CookProfile.objects.select_related('user').order_by('-average_rating')[:6]
    return render(request, 'core/home.html', {"featured": featured})


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            role = user.role
            if role == User.ROLE_COOK:
                CookProfile.objects.get_or_create(user=user, defaults={
                    'cuisine': '', 'dishes': '', 'experience_years': 0,
                    'hourly_rate': 0, 'location': '', 'bio': ''
                })
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('home')
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')


def cook_list(request: HttpRequest) -> HttpResponse:
    cooks = CookProfile.objects.select_related('user')
    q = request.GET.get('q', '').strip()
    cuisine = request.GET.get('cuisine', '').strip()
    location = request.GET.get('location', '').strip()
    min_rate = request.GET.get('min_rate', '').strip()
    max_rate = request.GET.get('max_rate', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()

    if q:
        cooks = cooks.filter(Q(user__username__icontains=q) | Q(dishes__icontains=q))
    if cuisine:
        cooks = cooks.filter(cuisine__icontains=cuisine)
    if location:
        cooks = cooks.filter(location__icontains=location)
    if min_rate:
        cooks = cooks.filter(hourly_rate__gte=min_rate)
    if max_rate:
        cooks = cooks.filter(hourly_rate__lte=max_rate)
    if min_rating:
        cooks = cooks.filter(average_rating__gte=min_rating)

    cuisines = CookProfile.objects.values_list('cuisine', flat=True).distinct()
    return render(request, 'core/cook_list.html', {
        'cooks': cooks,
        'cuisines': [c for c in cuisines if c],
        'filters': {
            'q': q,
            'cuisine': cuisine,
            'location': location,
            'min_rate': min_rate,
            'max_rate': max_rate,
            'min_rating': min_rating,
        }
    })


def cook_profile(request: HttpRequest, cook_id: int) -> HttpResponse:
    cook_user = get_object_or_404(User, id=cook_id, role=User.ROLE_COOK)
    profile = get_object_or_404(CookProfile, user=cook_user)
    reviews = Review.objects.filter(cook=cook_user).select_related('customer')
    return render(request, 'core/cook_profile.html', {
        'cook_user': cook_user,
        'profile': profile,
        'reviews': reviews,
        'booking_form': BookingForm(),
        'review_form': ReviewForm(),
    })


@login_required
def book_cook(request: HttpRequest, cook_id: int) -> HttpResponse:
    if not request.user.is_customer():
        messages.error(request, 'Only customers can place bookings.')
        return redirect('home')
    cook_user = get_object_or_404(User, id=cook_id, role=User.ROLE_COOK)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.cook = cook_user
            # Simple availability check by unique_together constraint will guard time slot
            try:
                booking.save()
            except Exception:
                messages.error(request, 'Selected time is no longer available.')
                return redirect('cook_profile', cook_id=cook_id)
            messages.success(request, 'Booking requested!')
            return redirect('customer_dashboard')
        messages.error(request, 'Please correct the errors in booking form.')
    else:
        form = BookingForm()
    return render(request, 'core/book_cook.html', {'cook_user': cook_user, 'form': form})


@login_required
def confirm_booking(request: HttpRequest, booking_id: int) -> HttpResponse:
    booking = get_object_or_404(Booking, id=booking_id)
    if not request.user.is_cook() or booking.cook != request.user:
        messages.error(request, 'Unauthorized action.')
        return redirect('home')
    booking.status = Booking.STATUS_CONFIRMED
    booking.save(update_fields=['status'])
    messages.success(request, 'Booking confirmed. Waiting for customer payment.')
    return redirect('cook_dashboard')


@login_required
def cancel_booking(request: HttpRequest, booking_id: int) -> HttpResponse:
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer and request.user != booking.cook:
        messages.error(request, 'Unauthorized action.')
        return redirect('home')
    booking.status = Booking.STATUS_CANCELLED
    booking.payment_status = Booking.PAYMENT_REFUNDED
    booking.save(update_fields=['status', 'payment_status'])
    messages.info(request, 'Booking cancelled and payment refunded.')
    if request.user.is_cook():
        return redirect('cook_dashboard')
    return redirect('customer_dashboard')


@login_required
def customer_dashboard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_customer():
        messages.error(request, 'Only customers can view this page.')
        return redirect('home')
    upcoming = Booking.objects.filter(customer=request.user, date__gte=date_class.today()).select_related('cook')
    past = Booking.objects.filter(customer=request.user, date__lt=date_class.today()).select_related('cook')
    return render(request, 'core/customer_dashboard.html', {
        'upcoming': upcoming,
        'past': past,
    })


@login_required
def cook_dashboard(request: HttpRequest) -> HttpResponse:
    if not request.user.is_cook():
        messages.error(request, 'Only cooks can view this page.')
        return redirect('home')
    requests_qs = Booking.objects.filter(cook=request.user).select_related('customer')
    earnings = requests_qs.filter(status=Booking.STATUS_COMPLETED).aggregate(total=Sum('duration_hours'))
    return render(request, 'core/cook_dashboard.html', {
        'bookings': requests_qs,
        'total_hours': earnings.get('total') or 0,
    })


@login_required
def add_review(request: HttpRequest, cook_id: int) -> HttpResponse:
    if not request.user.is_customer():
        messages.error(request, 'Only customers can add reviews.')
        return redirect('home')
    cook_user = get_object_or_404(User, id=cook_id, role=User.ROLE_COOK)
    # Require at least one completed and paid booking between this customer and cook
    has_completed = Booking.objects.filter(
        customer=request.user,
        cook=cook_user,
        status=Booking.STATUS_COMPLETED,
        payment_status=Booking.PAYMENT_PAID,
    ).exists()
    if not has_completed:
        messages.error(request, 'You can rate only after the service is completed and paid.')
        return redirect('customer_dashboard')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.cook = cook_user
            try:
                review.save()
            except Exception:
                messages.error(request, 'You have already reviewed this cook.')
                return redirect('customer_dashboard')
            # Update average rating
            avg = Review.objects.filter(cook=cook_user).aggregate(avg=Avg('rating'))['avg'] or 0
            CookProfile.objects.filter(user=cook_user).update(average_rating=avg)
            messages.success(request, 'Review added!')
            return redirect('customer_dashboard')
        messages.error(request, 'Please correct the errors in the review form.')
    return redirect('customer_dashboard')


@login_required
def complete_booking(request: HttpRequest, booking_id: int) -> HttpResponse:
    booking = get_object_or_404(Booking, id=booking_id)
    if not request.user.is_cook() or booking.cook != request.user:
        messages.error(request, 'Unauthorized action.')
        return redirect('home')
    if booking.status != Booking.STATUS_CONFIRMED:
        messages.error(request, 'Only confirmed bookings can be completed.')
        return redirect('cook_dashboard')
    booking.status = Booking.STATUS_COMPLETED
    booking.save(update_fields=['status'])
    messages.success(request, 'Booking marked as completed.')
    return redirect('cook_dashboard')


@login_required
def pay_booking(request: HttpRequest, booking_id: int) -> HttpResponse:
    booking = get_object_or_404(Booking, id=booking_id)
    if not request.user.is_customer() or booking.customer != request.user:
        messages.error(request, 'Unauthorized action.')
        return redirect('home')
    if booking.status != Booking.STATUS_CONFIRMED:
        messages.error(request, 'Booking must be confirmed by the cook before payment.')
        return redirect('customer_dashboard')
    if booking.payment_status == Booking.PAYMENT_PAID:
        messages.info(request, 'This booking is already paid.')
        return redirect('customer_dashboard')

    # Calculate amount (hourly_rate * duration)
    amount = 0
    if hasattr(booking.cook, 'cook_profile') and booking.cook.cook_profile:
        amount = (booking.cook.cook_profile.hourly_rate or 0) * booking.duration_hours

    if request.method == 'POST':
        # Simulate successful payment
        booking.payment_status = Booking.PAYMENT_PAID
        booking.save(update_fields=['payment_status'])
        messages.success(request, 'Payment successful!')
        return redirect('customer_dashboard')

    return render(request, 'core/payment.html', {
        'booking': booking,
        'amount': amount,
    })


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    user = request.user
    user_form = UserUpdateForm(instance=user)
    cook_form = None
    profile_obj = None
    if user.is_cook():
        profile_obj, _ = CookProfile.objects.get_or_create(user=user, defaults={
            'cuisine': '', 'dishes': '', 'experience_years': 0, 'hourly_rate': 0, 'location': '', 'bio': ''
        })
        cook_form = CookProfileForm(instance=profile_obj)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if user.is_cook():
            cook_form = CookProfileForm(request.POST, request.FILES, instance=profile_obj)
        if user_form.is_valid() and (cook_form.is_valid() if cook_form else True):
            user_form.save()
            if cook_form:
                cook_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'core/profile.html', {
        'user_form': user_form,
        'cook_form': cook_form,
        'profile_obj': profile_obj,
    })

