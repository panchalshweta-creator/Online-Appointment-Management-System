from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, AppointmentForm, ProfileForm, ServiceForm, ContactMessageForm
from .models import CustomUser, Profile, Service, Appointment, AvailabilitySlot, Category # Added Category
from django.db.models import Q
from datetime import date, timedelta

def home(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you shortly.')
            return redirect('home') # You might want to redirect to a specific part of the page, e.g., redirect('/#contact')
    else:
        form = ContactMessageForm()
    
    return render(request, 'appointment/home.html', {'form': form, 'categories': categories})

def category_businesses(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    businesses = Profile.objects.filter(category=category, is_approved=True)
    return render(request, 'appointment/category_businesses.html', {'category': category, 'businesses': businesses})

def business_detail(request, profile_id):
    business_profile = get_object_or_404(Profile, id=profile_id)
    services = Service.objects.filter(service_provider=business_profile)
    # Get availability slots for all services of this business
    availability_slots = AvailabilitySlot.objects.filter(service__service_provider=business_profile, date__gte=date.today(), is_booked=False).order_by('date', 'start_time')
    return render(request, 'appointment/business_detail.html', {
        'business_profile': business_profile,
        'services': services,
        'availability_slots': availability_slots
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            if user.role == 'business':
                Profile.objects.create(user=user, is_approved=True) # Set to True for easier testing
            login(request, user)
            if user.role == 'business':
                return redirect('business_profile_view')
            elif user.role == 'client':
                return redirect('client_dashboard')
            else:
                return redirect('home') # Fallback for any other role
    else:
        form = UserRegistrationForm()
    return render(request, 'appointment/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                if user.role == 'business':
                    return redirect('business_dashboard')
                elif user.role == 'client':
                    return redirect('client_dashboard')
                else: # Fallback, should not happen with proper role assignment
                    return redirect('home')
            else:
                return render(request, 'appointment/login.html', {'form': form, 'error_message': 'Invalid username or password.'})
    else:
        form = AuthenticationForm()
    return render(request, 'appointment/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
@user_passes_test(lambda user: user.role == 'client')
def client_dashboard(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'appointment/client_dashboard.html', {'appointments': appointments})

@login_required
@user_passes_test(lambda user: user.role == 'client')
def book_appointment(request):
    slot_id = request.GET.get('slot_id')
    initial_data = {}
    if slot_id:
        initial_data['availability_slot'] = get_object_or_404(AvailabilitySlot, id=slot_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            availability_slot = form.cleaned_data['availability_slot']
            if availability_slot.is_booked:
                messages.error(request, 'This time slot is already booked.')
                return redirect('book_appointment')
            
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.service = availability_slot.service
            appointment.status = 'Pending'
            appointment.save()

            availability_slot.is_booked = True
            availability_slot.save()
            
            messages.success(request, 'Appointment booked successfully! Status: Pending.')
            return redirect('client_dashboard')
    else:
        form = AppointmentForm(initial=initial_data)
        # Filter slots to only show available ones
        form.fields['availability_slot'].queryset = AvailabilitySlot.objects.filter(is_booked=False, date__gte=date.today())

    return render(request, 'appointment/book_appointment.html', {
        'form': form,
    })

@login_required
@user_passes_test(lambda user: user.role == 'client')
def client_appointments(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'appointment/client_appointments.html', {'appointments': appointments})

@login_required
@user_passes_test(lambda user: user.role == 'client')
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        if appointment.availability_slot:
            appointment.availability_slot.is_booked = False
            appointment.availability_slot.save()
        return redirect('client_appointments')
    return render(request, 'appointment/client_cancel_appointment.html', {'appointment': appointment})

@login_required
@user_passes_test(lambda user: user.role == 'client')
def client_profile(request):
    return render(request, 'appointment/client_profile.html')

@login_required
@user_passes_test(lambda user: user.role == 'client')
def respond_to_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            appointment.status = 'Rescheduled'
            appointment.save()
            messages.success(request, 'Reschedule accepted.')
        elif action == 'reject':
            appointment.status = 'Rejected'
            if appointment.availability_slot:
                appointment.availability_slot.is_booked = False
                appointment.availability_slot.save()
            appointment.save()
            messages.success(request, 'Reschedule rejected.')
        return redirect('client_dashboard')
    return redirect('client_dashboard')

@login_required
@user_passes_test(lambda user: user.role == 'business')
def business_dashboard(request):
    business_profile = get_object_or_404(Profile, user=request.user)
    pending_appointments = Appointment.objects.filter(service__service_provider=business_profile, status='Pending').order_by('availability_slot__date', 'availability_slot__start_time')
    accepted_appointments = Appointment.objects.filter(service__service_provider=business_profile, status__in=['Accepted', 'Rescheduled']).order_by('availability_slot__date', 'availability_slot__start_time')
    rejected_appointments = Appointment.objects.filter(service__service_provider=business_profile, status='Rejected').order_by('-updated_at')
    reschedule_requested = Appointment.objects.filter(service__service_provider=business_profile, status='Reschedule Requested').order_by('-updated_at')
    
    total_services = Service.objects.filter(service_provider=business_profile).count()
    total_appointments = Appointment.objects.filter(service__service_provider=business_profile).count()
    
    return render(request, 'appointment/business_dashboard.html', {
        'business_profile': business_profile,
        'pending_appointments': pending_appointments,
        'accepted_appointments': accepted_appointments,
        'rejected_appointments': rejected_appointments,
        'reschedule_requested': reschedule_requested,
        'total_services': total_services,
        'total_appointments': total_appointments,
    })

@login_required
@user_passes_test(lambda user: user.role == 'business')
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, service__service_provider__user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Accepted', 'Rejected', 'Completed', 'Cancelled']:
            appointment.status = new_status
            appointment.save()
            if new_status == 'Accepted' and appointment.availability_slot:
                appointment.availability_slot.is_booked = True
                appointment.availability_slot.save()
            if new_status in ['Rejected', 'Cancelled'] and appointment.availability_slot:
                appointment.availability_slot.is_booked = False
                appointment.availability_slot.save()
        return redirect('business_dashboard')
    return redirect('business_dashboard')

@login_required
@user_passes_test(lambda user: user.role == 'business')
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, service__service_provider__user=request.user)
    if request.method == 'POST':
        reschedule_date = request.POST.get('reschedule_date')
        reschedule_time = request.POST.get('reschedule_time')
        if reschedule_date and reschedule_time:
            appointment.reschedule_date = reschedule_date
            appointment.reschedule_time = reschedule_time
            appointment.status = 'Reschedule Requested'
            appointment.save()
            messages.success(request, 'Reschedule request sent to client.')
        return redirect('business_dashboard')
    return render(request, 'appointment/business_reschedule_appointment.html', {'appointment': appointment})

@login_required
@user_passes_test(lambda user: user.role == 'business')
def add_service(request):
    business_profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.service_provider = business_profile
            service.save()
            return redirect('business_dashboard') # Redirect to services list or dashboard
    else:
        form = ServiceForm()
    return render(request, 'appointment/add_service.html', {'form': form})

@login_required
@user_passes_test(lambda user: user.role == 'business')
def manage_services(request):
    business_profile = get_object_or_404(Profile, user=request.user)
    services = Service.objects.filter(service_provider=business_profile)
    return render(request, 'appointment/business_manage_services.html', {'services': services})

@login_required
@user_passes_test(lambda user: user.role == 'business')
def edit_service(request, service_id):
    business_profile = get_object_or_404(Profile, user=request.user)
    service = get_object_or_404(Service, id=service_id, service_provider=business_profile)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'appointment/business_edit_service.html', {'form': form, 'service': service})

@login_required
@user_passes_test(lambda user: user.role == 'business')
def delete_service(request, service_id):
    business_profile = get_object_or_404(Profile, user=request.user)
    service = get_object_or_404(Service, id=service_id, service_provider=business_profile)
    if request.method == 'POST':
        service.delete()
        return redirect('manage_services')
    return render(request, 'appointment/business_delete_service.html', {'service': service})

@login_required
@user_passes_test(lambda user: user.role == 'business')
def manage_availability(request, service_id):
    business_profile = get_object_or_404(Profile, user=request.user)
    service = get_object_or_404(Service, id=service_id, service_provider=business_profile)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        if date_str and start_time_str and end_time_str:
            AvailabilitySlot.objects.create(
                service=service,
                date=date_str,
                start_time=start_time_str,
                end_time=end_time_str
            )
        return redirect('manage_availability', service_id=service.id)

    availability_slots = AvailabilitySlot.objects.filter(service=service, date__gte=date.today()).order_by('date', 'start_time')
    return render(request, 'appointment/business_manage_availability.html', {'service': service, 'availability_slots': availability_slots})

@login_required
@user_passes_test(lambda user: user.role == 'business')
def delete_availability_slot(request, service_id, slot_id):
    business_profile = get_object_or_404(Profile, user=request.user)
    service = get_object_or_404(Service, id=service_id, service_provider=business_profile)
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, service=service)
    if request.method == 'POST':
        if not slot.is_booked: # Only delete if not booked
            slot.delete()
    return redirect('manage_availability', service_id=service.id)

@login_required
@user_passes_test(lambda user: user.role == 'business')
def business_profile_view(request):
    business_profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=business_profile)
        if form.is_valid():
            form.save()
            return redirect('business_profile_view')
    else:
        form = ProfileForm(instance=business_profile)
    return render(request, 'appointment/business_profile.html', {'form': form, 'business_profile': business_profile})
