from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import helpers.billing
from subscriptions.models import SubscriptionPrice, UserSubscription

# show details of the user subscription
@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    # sub_data = user_sub_obj.serialize()
    if request.method == 'POST':
        if user_sub_obj.stripe_id:
            sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id)
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, 'Your plan details have been refreshed.')
        return redirect(user_sub_obj.get_absolute_url())
    context = {
        'subscription': user_sub_obj,
    }
    return render(request, 'subscriptions/user_detail_view.html', context)

@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = helpers.billing.cancel_subscription(
                user_sub_obj.stripe_id,
                reason='User wanted to end',
            )
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, 'Your plan has been cancelled.')
        return redirect(user_sub_obj.get_absolute_url())
    context = {
        'subscription': user_sub_obj,
    }
    return render(request, 'subscriptions/user_cancel_view.html', context)

def subscription_price_view(request, interval='month'):
    qs = SubscriptionPrice.objects.filter(featured=True)
    inv_mo = SubscriptionPrice.IntervalChoises.MONTHLY
    inv_yr = SubscriptionPrice.IntervalChoises.YEARLY
    
    object_list = qs.filter(interval=inv_mo)
    url_path_name = 'pricing_interval'
    url_mo = reverse(url_path_name, kwargs={'interval': inv_mo})
    url_yr = reverse(url_path_name, kwargs={'interval': inv_yr})
    active = inv_mo
    
    if interval == inv_yr:
        active = inv_yr
        object_list = qs.filter(interval=inv_yr)
    
    context = {
        'object_list': object_list,
        'url_mo': url_mo,
        'url_yr': url_yr,
        'active': active
    }
    return render(request, 'subscriptions/pricing.html', context)