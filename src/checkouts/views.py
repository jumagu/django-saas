import logging
import stripe
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseForbidden
import helpers.billing

logger = logging.getLogger(__name__)

BASE_URL = settings.BASE_URL

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect('stripe_checkout_start')

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None
        
    if checkout_subscription_price_id is None or obj is None:
        return redirect('pricing')
    
    stripe_customer_id = request.user.customer.stripe_id
    success_url_path = reverse('stripe_checkout_end')
    pricing_url_path = reverse('pricing')
    success_url = f'{BASE_URL}{success_url_path}'
    cancel_url = f'{BASE_URL}{pricing_url_path}'
    stripe_price_id = obj.stripe_id

    url = helpers.billing.start_checkout_session(
        customer_id=stripe_customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        stripe_price_id=stripe_price_id
    )
    return redirect(url)

@login_required
def checkout_finalize_view(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('pricing')

    try:
        checkout_data = helpers.billing.get_checkout_customer_plan(session_id)
    except stripe.StripeError:
        checkout_data = None
    if checkout_data is None:
        messages.error(request, 'We could not verify your payment.')
        return redirect('pricing')

    customer_id = checkout_data.pop('customer_id')
    plan_id = checkout_data.pop('plan_id')
    sub_stripe_id = checkout_data.pop('sub_stripe_id')

    # The Stripe checkout session must belong to the logged-in user
    customer = getattr(request.user, 'customer', None)
    if customer is None or customer.stripe_id != customer_id:
        return HttpResponseForbidden()

    sub_obj = Subscription.objects.filter(subscriptionprice__stripe_id=plan_id).first()
    if sub_obj is None:
        return HttpResponseBadRequest('There was an error with your account, please contact us')

    user_sub_obj, _ = UserSubscription.objects.get_or_create(user=request.user)
    old_stripe_id = user_sub_obj.stripe_id

    # Already processed (e.g. the user refreshed the success page)
    if old_stripe_id == sub_stripe_id:
        return redirect(user_sub_obj.get_absolute_url())

    # Old checkout session: its subscription is no longer active, so leave the current one alone
    if checkout_data['status'] not in ('active', 'trialing'):
        return redirect(user_sub_obj.get_absolute_url())

    user_sub_obj.subscription = sub_obj
    user_sub_obj.stripe_id = sub_stripe_id
    user_sub_obj.user_cancelled = False
    for k, v in checkout_data.items():
        setattr(user_sub_obj, k, v)
    user_sub_obj.save()

    # Cancel the previous subscription after saving the new one. If Stripe fails here,
    # the old one is no longer in the database, so `sync_user_subs --clear-dangling` cancels it later.
    if old_stripe_id:
        try:
            helpers.billing.cancel_subscription(
                old_stripe_id,
                reason='Auto ended, new membership',
            )
        except stripe.StripeError:
            logger.exception('Could not cancel previous subscription %s', old_stripe_id)

    messages.success(request, 'Success! thank you for joining.')
    return redirect(user_sub_obj.get_absolute_url())
