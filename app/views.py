from datetime import datetime, date
from django import http
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.utils.text import slugify
from app.forms import CustomUserForm, CustomUserDisplayPhotoForm, OfferForm, CustomUserUpdateForm, CustomUserChangePasswordForm
from .models import CustomUser, Offer, Notification
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def home(request):
    context = None

    try:
        if request.user.is_authenticated:
            context = {
                'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None if request.user.is_authenticated else None
            }
    
    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/index.html', context)

def offers(request): 
    try:
        #check for vehicle type filter
        vehicle_type = request.GET.get('vt') 
        if vehicle_type:
            offers = Offer.objects.filter(vehicle_type=vehicle_type)
        else:
            offers = Offer.objects.filter(vehicle_type='L')

        #check for queries
        q = request.GET.get('q')
        if q:
            offers = offers.filter(
                Q(vehicle_name__icontains=q) | 
                Q(location__icontains=q) |
                Q(extra_details__icontains=q) |
                Q(owner__username__icontains=q)
            )
        

        # price bracket filter
        price_bracket = request.GET.get('price-bracket')
        if price_bracket is not None:
            match str(price_bracket):
                case '1':
                    offers = offers.filter(price__lte=10000)
                case '2':
                    offers = offers.filter(price__gte=10000).filter(price__lte=50000)
                case '3':
                    offers = offers.filter(price__gte=50000).filter(price__lte=100000)
                case '4':
                    offers = offers.filter(price__gte=100000)
        
        # location filter
        location = request.GET.get('location')
        if location is not None:
            match str(location):
                case 'harare':
                    offers = offers.filter(location__icontains='harare')
                case 'bulawayo':
                    offers = offers.filter(location__icontains='bulawayo')
                case 'victoria':
                    offers = offers.filter(location__icontains='victoria')
                case 'masvingo':
                    offers = offers.filter(location__icontains='masvingo')
        
        # mileage filter
        mileage = request.GET.get('mileage')
        if mileage is not None:
            match str(mileage):
                case '1':
                    offers = offers.filter(mileage__lte=10000)
                case '2':
                    offers = offers.filter(mileage__gte=10000).filter(mileage__lte=50000)
                case '3':
                    offers = offers.filter(mileage__gte=50000).filter(mileage__lte=100000)
                case '4':
                    offers = offers.filter(mileage__gte=100000)

        # brand filter
        brand = request.GET.get('brand')
        if brand is not None:
            match str(brand):
                case 'toyota':
                    offers = offers.filter(vehicle_name__icontains='toyota')
                case 'mercedes':
                    offers = offers.filter(vehicle_name__icontains='mercedes')
                case 'nissan':
                    offers = offers.filter(vehicle_name__icontains='nissan')
                case 'jeep':
                    offers = offers.filter(vehicle_name__icontains='jeep')

        context = {
            'query': q,
            'vehicle_type': vehicle_type,
            'price_bracket': price_bracket,
            'location': location,
            'mileage': mileage,
            'brand': brand,
            'offers': offers,
            'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None
        }
    
    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/offers.html', context)

def view_offer(request, slug): 
    try:
        offer = Offer.objects.get(slug=slug)
        if offer.owner != request.user:
            offer.view_count += 1
            offer.save(update_fields=['view_count'])

        images = [
                image for image in 
                [
                    offer.image1, offer.image2, 
                    offer.image3, offer.image4, 
                    offer.image5, offer.image6, 
                    offer.image7
                ] 
                if bool(image)
            ]
        
        context = {
            'offer': Offer.objects.get(slug=slug),
            'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None,
            'images': images,
        }
    
    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/view-offer.html', context)

@login_required(login_url='user_login')
def delete_offer(request, slug): 
    try:
        offer = Offer.objects.get(slug=slug)
        vehicle_name = offer.vehicle_name
        offer.delete()
        
        # create relevant notification
        Notification.objects.create(
            owner = request.user,
            title = "One of your offers was removed.",
            body = f"Your '{vehicle_name}' offer was removed on {date.today()} \
                at {datetime.today().time()}. If this was not you, \
                <a href=''>click here</a> to get a password reset link sent to your email. \
                This will logout your account on every device.",
            icon = 'ET'
        )
        messages.info(request, f"Your '{vehicle_name}' offer was removed.")
    
    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return redirect(request.user.get_absolute_url())

def create_offer(request):
    try:    
        if not request.user.is_authenticated:
            messages.info(request, 'Lets first log into your account.')
            return redirect('user-login')

        if request.method == 'POST':
            form = OfferForm(request.POST, request.FILES)
        
            if form.is_valid():
                offer = form.save()
                offer.owner = request.user
                offer.slug = slugify(offer.vehicle_name + "-" + str(offer.id))
                
                # count images
                count = 1
                for image in [offer.image2, offer.image3, offer.image4, offer.image5, offer.image6, offer.image7]:
                    if bool(image):
                        count += 1
                offer.image_count = count 
                offer.save()

                # create relevant notification
                Notification.objects.create(
                    owner = request.user,
                    title = "New offer was uploaded successfully",
                    body = "Offer for {} uploaded on {}. \
                        <a href='{}'>View</a>".format(offer.vehicle_name, offer.date.date(), offer.get_absolute_url()),
                    icon = 'I'
                )

                messages.success(request, 'Your offer was uploaded successfully.')
                return redirect('offers')
            else:
                messages.error(request, form.errors.as_text(), 'danger')

        context = {
            'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None,
            'action': 'Post your vehicle for sale'
        }

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/create-offer.html', context)

def account(request, slug):
    try: 
        context = {
            'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None,
            'user': CustomUser.objects.get(slug=slug)
        }

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/account.html', context)

def user_signup(request):
    try:
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

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/signup.html', {'action': 'Signup'})

def user_login(request):
    try:
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

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')
    
    return render(request, 'app/login.html')

@login_required(login_url='user_login')
def user_logout(request):
    try:
        logout(request)
        messages.warning(request, 'You were logged out.')

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
    
    return redirect('home')

@login_required(login_url='user_login')
def user_notifications(request):
    try:
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

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')
    
    return render(request, 'app/notifications.html', context)

@login_required(login_url='user_login')
def change_display_photo(request):
    try:
        if request.method == 'POST':
            form = CustomUserDisplayPhotoForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your display photo was updated successfully.')
            else:
                messages.error(request, form.errors.as_text(), 'danger')

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return redirect(request.user.get_absolute_url())

@login_required(login_url='user_login')
def update_profile(request):
    try:
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
        
    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/signup.html', {'action': 'Update account'})

@login_required(login_url='user_login')
def user_settings(request):
    return render(request, 'app/settings.html')

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

    return render(request, 'app/settings.html')

@login_required(login_url='user_login')
def change_password(request):
    try:
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

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/settings.html')

@login_required(login_url='user_login')
def edit_offer(request, slug):
    try:
        offer = Offer.objects.get(slug=slug)
        if request.method == 'POST':
            form = OfferForm(request.POST, request.FILES, instance=offer)
            if form.is_valid():
                offer = form.save()
                offer.slug = slugify(offer.vehicle_name + "-" + str(offer.id))
                offer.owner = request.user
                
                # count images
                count = 1
                for image in [offer.image2, offer.image3, offer.image4, offer.image5, offer.image6, offer.image7]:
                    if bool(image):
                        count += 1
                offer.image_count = count 
                offer.save()

                # create relevant notification
                Notification.objects.create(
                    owner = request.user,
                    title = f"'{offer.vehicle_name}' offer was updated successfully",
                    body = f"Your offer for a {offer.vehicle_name} was updated. \
                        <a href='{offer.get_absolute_url()}'>View</a>",
                    icon = 'I'
                )

                messages.success(request, 'Your offer was updated successfully.')
                return redirect(offer.get_absolute_url())
            else:
                messages.error(request, form.errors.as_text(), 'danger')
        
        context = {
            'action': 'Update offer',
            'offer': offer
        }

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/create-offer.html', context)

def enquire(request, slug):
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'Lets first log into your account.')
            return redirect('user-login')
            
        offer = Offer.objects.get(slug=slug)

        if request.method == 'POST':
            offerprice = request.POST.get('offerprice')
            offerdetails = request.POST.get('offerdetails')
            offerdetails = '"' + offerdetails + '"' if offerdetails != 'type something...' else ''
            enquirer = request.user
            phone_number = 'phone: ' + str(enquirer.phone_number) if enquirer.phone_number else ''
            email_address = 'email: ' + enquirer.email

            enquiry = """
                <a href='{}'>{}</a> has made an offer on your '{}' advert. The offer price 
                is USD {}. Their contact details are {}. Other details: {}. {}.  
            """.format(
                    enquirer.get_absolute_url(),
                    enquirer.username,
                    offer.vehicle_name,
                    offerprice,
                    phone_number + ' ' + email_address,
                    offerdetails,
                    datetime.today().date()
                )
            
            # create relevant notification to owner of offer
            Notification.objects.create(
                owner = offer.owner,
                title = "Someone enquired about your offer.",
                body = enquiry,
                icon = 'E'
            )
            
            # create relevant notification to enquirer
            Notification.objects.create(
                owner = enquirer,
                title = "Enquiry sent successfully.",
                body = f"Your enquiry for a '{offer.vehicle_name}' was sent to \
                    <a href='{offer.owner.get_absolute_url()}'>{offer.owner.username}</a> \
                    successfully. Feel free to contact \
                    them if you do not get a response in time.",
                icon = 'E'
            )

            enquirer.enquired.add(offer)
            enquirer.save()
            messages.success(request, 'Your enquiry was sent successfully')
            return redirect(offer.get_absolute_url())
        context = {
            'offer': offer,
            'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None,
        }

    except Exception as e:
        messages.warning(request, 'SYSTEM ERROR. ' + str(e))
        return redirect('/')

    return render(request, 'app/enquire.html', context)


