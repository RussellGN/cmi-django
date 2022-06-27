import re
from django.http import HttpResponse
from datetime import datetime, date
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.text import slugify
from app.forms import OfferForm
from .models import Offer
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import  Notification
from django.core.paginator import Paginator

def home(request):
    context = None

    if request.user.is_authenticated:
        context = {
            'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None if request.user.is_authenticated else None
        }
    
    return render(request, 'app/index.html', context)

def offers(request): 

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

    # pagination
    p = Paginator(offers, 5)  
    page_number = request.GET.get('page')
    page_number = page_number if page_number else 1
    
    if int(page_number) > int(p.num_pages) or int(page_number) == 0:
        page_number = 1
    page_obj = p.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': q,
        'vehicle_type': vehicle_type,
        'price_bracket': price_bracket,
        'location': location,
        'mileage': mileage,
        'brand': brand,
        # 'offers': offers,
        'new_notifications': Notification.objects.filter(owner=request.user, view_count=0) if request.user.is_authenticated else None
    }

    return render(request, 'app/offers.html', context)

def view_offer(request, slug): 
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

    return render(request, 'app/view-offer.html', context)

@login_required(login_url='user_login')
def delete_offer(request, slug): 
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

    return redirect(request.user.get_absolute_url())

def create_offer(request):
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

    return render(request, 'app/create-offer.html', context)

@login_required(login_url='user_login')
def edit_offer(request, slug):
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

    return render(request, 'app/create-offer.html', context)

def enquire(request, slug):
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

    return render(request, 'app/enquire.html', context)


