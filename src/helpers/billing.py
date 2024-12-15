# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
from decouple import config

DJANGO_DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='', cast=str)

if 'sk_test' in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Invalid stripe key for prod")

stripe.api_key = STRIPE_SECRET_KEY


def create_customer(name='', email='', metadata={}, raw=False):  
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata,
    )
    if raw:
        return response
    return response.id # stripe customer id

def create_product(name='', metadata={}, raw=False):
    response = stripe.Product.create(name=name, metadata=metadata)
    if raw:
        return response
    return response.id # stripe product id

def create_price(
    currency='usd',
    unit_amount='9999',
    interval='month',
    product=None,
    metadata={},
    raw=False,
):
    if product is None:
        return None
    response = stripe.Price.create(
                    currency=currency,
                    unit_amount=unit_amount,
                    recurring={'interval': interval},
                    product=product,
                    metadata=metadata,
                )
    if raw:
        return response
    return response.id # stripe product id

def start_checkout_session(
    customer_id='',
    success_url='',
    stripe_price_id='',
    cancel_url='',
    raw=False
):
    if not success_url.endswith('?session_id={CHECKOUT_SESSION_ID}'):
        success_url = f'{success_url}' + '?session_id={CHECKOUT_SESSION_ID}'
    response = stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": stripe_price_id, "quantity": 1}],
        mode="subscription",
    )
    if raw:
        return response
    return response.url

def get_checkout_session(stripe_id, raw=False):
    response = stripe.checkout.Session.retrieve(stripe_id)
    if raw:
        return response
    return None

def get_subscription(stripe_id, raw=False):
    response = stripe.Subscription.retrieve(stripe_id)
    if raw:
        return response
    return None

def cancel_subscription(stripe_id, reason='', feedback='other', raw=False):
    response = stripe.Subscription.cancel(
        stripe_id,
        cancellation_details = {
            'comment': reason,
            'feedback': feedback,
        }
    )
    if raw:
        return response
    return None

def get_checkout_customer_plan(session_id):
    checkout_res = get_checkout_session(stripe_id=session_id, raw=True)
    customer_id = checkout_res.customer
    sub_stripe_id = checkout_res.subscription
    sub_res = get_subscription(sub_stripe_id, raw=True)
    sub_plan = sub_res.plan
    return customer_id, sub_plan.id, sub_stripe_id