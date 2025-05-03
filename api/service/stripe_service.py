import os
import stripe
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from api.database import users_collection
from api.database import db
from models.stripe_customer import StripeCustomer

# Initialize Stripe with your API keys
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Product IDs
MONTHLY_PRODUCT_ID = os.environ.get('STRIPE_MONTHLY_PRODUCT_ID')
YEARLY_PRODUCT_ID = os.environ.get('STRIPE_YEARLY_PRODUCT_ID')

# Collection for storing Stripe customers
stripe_customers = db['stripe_customers']
subscriptions_collection = db['subscription']

def get_subscription_prices() -> Dict[str, Optional[Dict[str, Any]]]:
    """Get the current prices for subscription plans."""
    # Ensure product IDs are set
    if MONTHLY_PRODUCT_ID is None or YEARLY_PRODUCT_ID is None:
        raise ValueError("Stripe product IDs are not set in environment variables.")
    # Fetch prices for our products
    monthly_prices = stripe.Price.list(product=MONTHLY_PRODUCT_ID)
    yearly_prices = stripe.Price.list(product=YEARLY_PRODUCT_ID)
    
    prices: Dict[str, Optional[Dict[str, Any]]] = {
        'monthly': None,
        'yearly': None
    }
    
    # Get the active price for each product
    if monthly_prices.data:
        monthly_price = monthly_prices.data[0]
        prices['monthly'] = {
            'id': monthly_price.id,
            'amount': (monthly_price.unit_amount / 100) if monthly_price.unit_amount is not None else 0,  # Convert from cents
            'currency': monthly_price.currency,
            'product_id': monthly_price.product
        }
        
    if yearly_prices.data:
        yearly_price = yearly_prices.data[0]
        prices['yearly'] = {
            'id': yearly_price.id,
            'amount': (yearly_price.unit_amount / 100) if yearly_price.unit_amount is not None else 0,  # Convert from cents
            'currency': yearly_price.currency,
            'product_id': yearly_price.product
        }
    
    return prices

def create_stripe_customer(user_id: ObjectId, email: str, name: str) -> str:
    """Create a new customer in Stripe and return the customer ID."""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                'user_id': str(user_id)
            }
        )
        
        # Save the customer information in our database
        stripe_customer = {
            'user_id': user_id,
            'stripe_customer_id': customer.id,
        }
        stripe_customers.insert_one(stripe_customer)
        
        return customer.id
    except Exception as e:
        print(f"Error creating Stripe customer: {e}")
        raise

def get_stripe_customer_by_user_id(user_id: ObjectId) -> Optional[StripeCustomer]:
    """Get Stripe customer information by user ID."""
    result = stripe_customers.find_one({'user_id': user_id})
    if result:
        return StripeCustomer(
            _id=result['_id'],
            user_id=result['user_id'],
            stripe_customer_id=result['stripe_customer_id'],
            stripe_subscription_id=result.get('stripe_subscription_id'),
            default_payment_method=result.get('default_payment_method')
        )
    return None

def create_checkout_session(user_id: ObjectId, price_id: str, success_url: str, cancel_url: str) -> str:
    """Create a Stripe checkout session and return the session URL."""
    # Get customer information
    stripe_customer = get_stripe_customer_by_user_id(user_id)
    
    if not stripe_customer:
        # Get user details
        user = users_collection.find_one({'_id': user_id})
        if not user:
            raise ValueError("User not found")
        
        # Create a new Stripe customer
        customer_id = create_stripe_customer(user_id, user['email'], user['username'])
    else:
        customer_id = stripe_customer.stripe_customer_id
        
    # Create checkout session
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card', 'paypal', 'revolut_pay', 'link', 'amazon_pay'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user_id)
            },
            # Configurar para usar el dominio personalizado
            custom_text={
                'submit': {
                    'message': 'Estamos procesando tu suscripción con updateme.dev'
                }
            }
        )
        
        # Ensure URL is returned
        url = session.url
        if not url:
            raise Exception("Failed to retrieve checkout session URL")
        return url
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        raise

def setup_custom_branding():
    """
    Configura el branding personalizado para el dominio de Stripe.
    Esta función debe ejecutarse una sola vez para configurar tu dominio personalizado.
    Guarda el ID de configuración como variable de entorno.
    """
    try:
        # Crea la configuración personalizada para el portal de facturación
        configuration = stripe.billing_portal.Configuration.create(
            business_profile={
                "headline": "UpdateMe - Gestiona tu suscripción",
                "privacy_policy_url": "https://updateme.dev/privacy-policy",
                "terms_of_service_url": "https://updateme.dev/terms-and-conditions",
            },
            features={
                "customer_update": {
                    "allowed_updates": ["email", "address", "shipping", "phone", "tax_id"],
                    "enabled": True,
                },
                "invoice_history": {"enabled": True},
                "payment_method_update": {"enabled": True},
            },
        )
        
        print(f"Configuración de portal creada con ID: {configuration.id}")
        return configuration.id
    except Exception as e:
        print(f"Error al configurar el branding personalizado: {e}")
        raise

def create_portal_session(customer_id: str, return_url: str) -> str:
    """Create a Stripe customer portal session."""
    try:
        # Intenta obtener la configuración del portal desde las variables de entorno
        configuration_id = os.environ.get('STRIPE_PORTAL_CONFIGURATION_ID')
        
        session_params = {
            "customer": customer_id,
            "return_url": return_url,
        }
        
        # Añadir la configuración personalizada si está disponible
        if configuration_id:
            session_params["configuration"] = configuration_id
            
        # Create billing portal session with explicit keyword args to satisfy type checker
        if "configuration" in session_params:
            session = stripe.billing_portal.Session.create(
                customer=session_params["customer"],
                return_url=session_params["return_url"],
                configuration=session_params["configuration"],
            )
        else:
            session = stripe.billing_portal.Session.create(
                customer=session_params["customer"],
                return_url=session_params["return_url"],
            )
        
        return session.url
    except Exception as e:
        print(f"Error creating portal session: {e}")
        raise

def handle_checkout_session_completed(event_data):
    """Process checkout.session.completed: store subscription, update user and record transaction."""
    session = event_data['object']
    # Only handle subscription mode sessions
    if getattr(session, 'mode', None) == 'subscription':
        user_id = ObjectId(session.metadata.get('user_id', ''))
        # Ensure stripe customer exists
        stripe_customers.update_one({'user_id': user_id}, {'$setOnInsert': {'stripe_customer_id': session.customer}}, upsert=True)
        # --- CORRECCIÓN: obtener SIEMPRE el id de la suscripción como string ---
        sub_id = session.subscription.id if hasattr(session.subscription, 'id') else session.subscription
        sub = stripe.Subscription.retrieve(sub_id, expand=['items.data', 'default_payment_method'])
        # Billing info
        items = sub.items.data if hasattr(sub, 'items') and sub.items and hasattr(sub.items, 'data') else []
        plan = items[0].plan if items else None
        interval = getattr(plan, 'interval', 'monthly')
        price_amount = (plan.amount / 100) if plan and hasattr(plan, 'amount') and plan.amount is not None else 0
        # Period dates
        start = datetime.fromtimestamp(getattr(sub, 'current_period_start', 0))
        end = datetime.fromtimestamp(getattr(sub, 'current_period_end', 0))
        # Default payment method
        dpm_obj = getattr(sub, 'default_payment_method', None)
        dpm_id = getattr(dpm_obj, 'id', None)
        # Save subscription record
        sub_doc = {
            'status': 'active',
            'start_date': start,
            'end_date': end,
            'renewal_date': end,
            'payment_method_id': dpm_id,
            'price': price_amount,
            'interval': interval
        }
        sub_mongo = subscriptions_collection.insert_one(sub_doc).inserted_id
        # Update user role and subscription ref
        users_collection.update_one({'_id': user_id}, {'$set': {'role': 'paid', 'subscription': sub_mongo}})
        # Update customer record
        stripe_customers.update_one({'user_id': user_id}, {'$set': {'stripe_subscription_id': sub.id, 'default_payment_method': dpm_id}})
        # Record transaction
        db['transactions'].insert_one({
            'user_id': user_id,
            'payment_method': dpm_id,
            'amount': price_amount,
            'currency': sub.currency,
            'status': 'successful',
            'provider_transacction_id': sub.id,
            'created_at': datetime.utcnow()
        })

def handle_subscription_updated(event_data):
    """Process customer.subscription.updated webhook event."""
    subscription = event_data['object']
    
    # Get the Stripe customer associated with this subscription
    stripe_customer = stripe_customers.find_one({'stripe_subscription_id': subscription.id})
    
    if not stripe_customer:
        print(f"No customer found for subscription {subscription.id}")
        return
    
    user_id = stripe_customer['user_id']
    
    # Get the user's subscription in our database
    user = users_collection.find_one({'_id': user_id})
    if not user or not user.get('subscription'):
        print(f"User {user_id} has no subscription record")
        return
        
    subscription_id = user['subscription']
    
    # Update subscription status
    status = 'active' if subscription['status'] == 'active' else 'canceled'
    
    current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
    current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
    
    # Update subscription record
    subscriptions_collection.update_one(
        {'_id': subscription_id},
        {
            '$set': {
                'status': status,
                'start_date': current_period_start,
                'renewal_date': current_period_end,
                'price': subscription['items']['data'][0]['plan']['amount'] / 100 if subscription['items']['data'] else 0,
            }
        }
    )
    
def handle_subscription_deleted(event_data):
    """Process customer.subscription.deleted webhook event."""
    subscription = event_data['object']
    
    # Get the customer associated with this subscription
    stripe_customer = stripe_customers.find_one({'stripe_subscription_id': subscription.id})
    
    if not stripe_customer:
        print(f"No customer found for subscription {subscription.id}")
        return
        
    user_id = stripe_customer['user_id']
    
    # Get the user's subscription in our database
    user = users_collection.find_one({'_id': user_id})
    if not user or not user.get('subscription'):
        print(f"User {user_id} has no subscription record")
        return
        
    subscription_id = user['subscription']
    
    # Mark subscription as canceled
    subscriptions_collection.update_one(
        {'_id': subscription_id},
        {'$set': {'status': 'canceled'}}
    )
    
    # Update user role back to free
    users_collection.update_one(
        {'_id': user_id},
        {'$set': {'role': 'free'}}
    )
    
    # Remove subscription_id from stripe_customer
    stripe_customers.update_one(
        {'user_id': user_id},
        {'$unset': {'stripe_subscription_id': ""}}
    )