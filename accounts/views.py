from datetime import datetime, date
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.text import slugify
from .forms import CustomUserForm, CustomUserDisplayPhotoForm, CustomUserUpdateForm, CustomUserChangePasswordForm
from .models import CustomUser, Notification
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

def account(request, slug):
    context = {
        'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None,
        'user': CustomUser.objects.get(slug=slug)
    }

    return render(request, 'accounts/account.html', context)

def user_signup(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in as '" + request.user.username + "'. Please logout first to create another account.")
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
    
        if form.is_valid():
            user = form.save()
            user.slug = slugify(user.username + "-" + str(user.id))
            if user.about == "A short description of yourself/your dealership": 
                user.about = ''
            user.save()
            login(request, user)            

            # create relevant notifications
            Notification.objects.create(
                owner = user,
                title = "Getting started guide 1.",
                body = "Welcome to cars.zim {}. Get started by creating your first offer \
                    <a href={% url 'create-offer' %}>Here</a>".format(user.username),
                icon = 'S'
            )
            Notification.objects.create(
                owner = user,
                title = "Getting started guide 2.",
                body = "<a href={}>Upload</a> a display photo and <a href={% url 'user-settings' %}>\
                    tweak your settings</a> to your likeness.".format(user.get_absolute_url()),
                icon = 'S'
            )

            messages.success(request, 'Welcome to cars.zim ' + user.username + ". Your account was created successfully.")
            return redirect(user.get_absolute_url())
        else:
            messages.error(request, form.errors.as_text(), 'danger')

    return render(request, 'accounts/signup.html', {'action': 'Signup'})

def user_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in as '" + request.user.username + "'. Logout if you wish to log into another account.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user != None:
            login(request, user)
            messages.success(request, "Welcome back! Logged in as '" + user.username + "'.")
            return redirect(user.get_absolute_url())
        else:
            messages.error(request, "Incorrect password or Username", 'danger')        
    
    return render(request, 'accounts/login.html')

@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    messages.warning(request, 'You were logged out.')

    return redirect('home')

@login_required(login_url='user_login')
def user_notifications(request):
    notifications = Notification.objects.filter(owner=request.user)
    
    count = 0
    for notification in notifications:
        if notification.view_count > 8:
            notification.delete()
            count += 1
        else:
            notification.view_count += 1
            notification.save()

    context = {
        'notifications': Notification.objects.filter(owner=request.user)
    }

    if count:
        suffix = 's were' if count > 1 else ' was' 
        messages.info(request, f'{count} old notification{suffix} removed.')

    return render(request, 'accounts/notifications.html', context)

@login_required(login_url='user_login')
def change_display_photo(request):
    if request.method == 'POST':
        form = CustomUserDisplayPhotoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your display photo was updated successfully.')
        else:
            messages.error(request, form.errors.as_text(), 'danger')

    return redirect(request.user.get_absolute_url())

@login_required(login_url='user_login')
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            user.slug = slugify(user.username + "-" + str(user.id))
            if not user.phone_number: 
                user.notification_inbox = 'E'
            if user.about == "A short description of yourself/your dealership": 
                user.about = ''
            user.save()
            messages.success(request, 'Your account details were updated successfully.')
            return redirect(user.get_absolute_url())
        else:
            messages.error(request, form.errors.as_text(), 'danger')

    return render(request, 'accounts/signup.html', {'action': 'Update account'})

@login_required(login_url='user_login')
def user_settings(request):
    return render(request, 'accounts/settings.html')

@login_required(login_url='user_login')
def update_inbox_settings(request):
    try:
        if request.method == 'POST':
            selected_inbox = request.POST.get('notification_inbox')        
            request.user.notification_inbox = selected_inbox
            request.user.save()

    except:
        messages.error(request, 'Failed to update notification settings', 'danger')
        return redirect('/')

    else:
        messages.success(request, 'Your notification settings were updated successfully.')

    return render(request, 'accounts/settings.html')

@login_required(login_url='user_login')
def change_password(request):
    if request.method == 'POST':
        form = CustomUserChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            logout(request)
            user = form.save()
            login(request, user)
            messages.success(request, 'Password changed successfully.')

            # create relevant notification
            Notification.objects.create(
                owner = request.user,
                title = "Your password was recently changed.",
                body = "Your password was changed on {} at {}. If this was not you, \
                    <a href=''>click here</a> to get a password reset link sent to your email".format(
                            date.today(),
                            datetime.today().time()
                        ),
                icon = 'ET'
            )
        
        else:
            messages.error(request, form.errors.as_text(), 'danger')
            # create relevant notification
            Notification.objects.create(
                owner = request.user,
                title = "There was an attempt to change your password.",
                body = "There was an attempt to change your password \
                        on {} at {}. If this was not you, <a href=''>click here</a> \
                        to get a password reset link sent to your email. \
                        This will logout your account on any device".format(
                            date.today(),
                            datetime.today().time()
                        ),
                icon = 'ET'
            )

    return render(request, 'accounts/settings.html')


