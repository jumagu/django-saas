from django.urls import reverse
from django.shortcuts import render
from subscriptions.models import SubscriptionPrice


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