
import requests
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from cart.models import Cart, CartItem
from cart.views import _cart_id
from orders.models import Order, OrderItems, ProfileAddress

from .forms import (AddressForm, RegistrationForm, UserForm, UserProfileForm,
                    VerifyForm, VerifyotpForm, otploginForm)
from .models import Account, UserProfile
from .verify import check, send


# Create your views here.
@never_cache
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            if Account.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'Phone number already exists')

            else:
                user = Account.objects.create_user(
                    first_name=first_name, last_name=last_name, email=email, username=username, password=password)
                user.phone_number = phone_number
                user.save()
                request.session['phone_number'] = phone_number
                send(form.cleaned_data.get('phone_number'))
                return redirect('accounts:verify')
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def verifyotp(request):
    if request.method == 'POST':
        form = VerifyotpForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone_number = request.session['phone_number']

            if check(phone_number, code):
                print('fdgsdfgdsfgdfgsrf')
                user = Account.objects.get(phone_number=phone_number)

                if user is not None:
                    auth.login(request, user)
                    messages.success(request, 'you are now logged in')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid credentials')
                    return redirect('accounts:login_page')
    else:
        form = VerifyForm()
    return render(request, 'accounts/verify.html', {'form': form})


def verify_code(request):
    if request.method == 'POST':

        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            phone_number = request.session['phone_number']
            print('fdgsdfgdsfgdfgsrf')
            if check(phone_number, code):
                user = Account.objects.get(phone_number=phone_number)
                user.is_active = True
                user.save()
                return redirect('accounts:login_page')
    else:
        form = VerifyForm()
    return render(request, 'accounts/verify.html', {'form': form})


@never_cache
def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)

            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(
                        cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                        cart_item = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
                except:
                    pass
                auth.login(request, user)
                messages.success(request, 'you are now logged in')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)

                except:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('accounts:login_page')
        return render(request, 'accounts/login.html')


def otplogin(request):
    if request.method == 'POST':
        form = otploginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']

            if Account.objects.filter(phone_number=phone_number).exists():

                user = Account.objects.get(phone_number=phone_number)
                request.session['phone_number'] = phone_number
                send(form.cleaned_data.get('phone_number'))
                return redirect('accounts:verifyotp')

            else:
                messages.error(request, "Account Doesnot exist!")
        else:
            messages.error(request, "Enter a Valid Phone Number!")
    return render(request, 'accounts/otp_login.html')


@login_required(login_url='accounts:login_page')
@never_cache
def logout(request):
    auth.logout(request)
    messages.success(request, 'you are logged out')
    return redirect('accounts:login_page')


def activate(request, uidb64, token):

    try:
        uid = uidb64
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "congratulations your account has been varified")
        return redirect('accounts:login_page')
    else:
        messages.error(request, "Invalid Activation link!")
        return redirect("register")


@login_required(login_url='accounts:login_page')
def dashboard(request):
    orders = Order.objects.order_by(
        "-created_at").filter(user_id=request.user.id)
    orders_count = orders.count
    userprofile = UserProfile.objects.filter(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

# add address


def add_address(request):
    if request.method == "POST":
        user = request.user
        address_line_1 = request.POST['address_line_1']
        address_line_2 = request.POST['address_line_2']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        pincode = request.POST['pincode']
        ins = UserProfile(user=user, address_line_1=address_line_1,
                             address_line_2=address_line_2, city=city, state=state, country=country, pincode=pincode)
        ins.save()

    return render(request, 'accounts/add_address.html')
# add address ends here


def address_list(request):
    defualt_add = UserProfile.objects.filter(user=request.user)
    context = {
        'ins': defualt_add
    }
    return render(request, 'accounts/address_list.html', context)


def edit_address(request, address_id):
    profile = UserProfile.objects.get(id=address_id)
    if request.method == "POST":
        profile_form = UserProfileForm(
            request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile Updated.')
            return redirect('accounts:address_list')
    else:
        profile_form = AddressForm(instance=profile)
    context = {
        'profile_form': profile_form,
        "userprofile": profile,
    }
    return render(request, 'accounts/edit_address.html', context)


def edit_profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile Updated.')
            return redirect('accounts:edit_profile')
    else:
        user_form = UserForm(instance=request.user)
    context = {
        'user_form': user_form,
    }
    return render(request, 'accounts/edit_profile.html', context)
# Change Password View


@login_required(login_url='accounts:login_page')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password Changed Successfully")
                return redirect('change_password')
            else:
                messages.error(request, "Wrong Password")
                return redirect('change_password')
        else:
            messages.error(request, "Passwords donot Match")
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


login_required(login_url='accounts:login_page')


def order_detail(request, tracking_no):
    order_detail = OrderItems.objects.filter(order__tracking_no=tracking_no)
    order = Order.objects.get(tracking_no=tracking_no)
    subtotal = 0
    for i in order_detail:
        subtotal += i.price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    # __order_number means this order's order number
    return render(request, 'accounts/order_detail.html', context)
