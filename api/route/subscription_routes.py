from flask import Blueprint, request, jsonify, url_for, redirect, session, render_template
import os
import stripe
from bson import ObjectId
from api.service.stripe_service import (
    get_subscription_prices,
    create_checkout_session,
    create_portal_session,
    get_stripe_customer_by_user_id,
    handle_checkout_session_completed,
    handle_subscription_updated,
    handle_subscription_deleted
)
from api.auth import login_required

subscription_routes = Blueprint('subscription_routes', __name__, url_prefix='/subscription')

# Stripe webhook secret
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

@subscription_routes.route('/prices', methods=['GET'])
def get_prices():
    """Get current subscription prices."""
    try:
        prices = get_subscription_prices()
        return jsonify({'success': True, 'prices': prices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_routes.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Create a checkout session for subscription."""
    try:
        data = request.json
        price_id = data.get('priceId')
        
        if not price_id:
            return jsonify({'success': False, 'error': 'Price ID is required'}), 400
        
        user_id = ObjectId(session['user_id'])
        
        # Create success and cancel URLs
        success_url = url_for('api.subscription_routes.checkout_success', _external=True)
        cancel_url = url_for('api.subscription_routes.checkout_cancel', _external=True)
        
        # Create checkout session
        checkout_url = create_checkout_session(user_id, price_id, success_url, cancel_url)
        
        return jsonify({'success': True, 'checkoutUrl': checkout_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_routes.route('/success', methods=['GET'])
@login_required
def checkout_success():
    """Handle successful checkout: update user role and redirect to dashboard."""
    session_id = request.args.get('session_id')
    try:
        # Retrieve the Stripe checkout session and process subscription
        checkout_session = stripe.checkout.Session.retrieve(session_id, expand=['subscription'])
        handle_checkout_session_completed({'object': checkout_session})
        # Redirect to dashboard after subscription is processed
        return redirect(url_for('main.page.dashboard'))
    except Exception as e:
        # Return error if processing fails
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_routes.route('/cancel', methods=['GET'])
def checkout_cancel():
    """Handle canceled checkout."""
    return render_template('subscription_cancel.html')

@subscription_routes.route('/portal', methods=['POST'])
@login_required
def customer_portal():
    """Create a customer portal session."""
    try:
        user_id = ObjectId(session['user_id'])
        
        # Get Stripe customer
        stripe_customer = get_stripe_customer_by_user_id(user_id)
        if not stripe_customer:
            return jsonify({'success': False, 'error': 'No Stripe customer found'}), 404
        
        # Create return URL
        return_url = url_for('main.page.dashboard', _external=True)
        
        # Create portal session
        portal_url = create_portal_session(stripe_customer.stripe_customer_id, return_url)
        
        return jsonify({'success': True, 'portalUrl': portal_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@subscription_routes.route('/webhooks/stripe', methods=['POST'])  # remains outside subscription prefix
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
            event_data = event['data']
            event_type = event['type']
        else:
            # For development without webhook signing
            data = request.json
            event_data = data['data']
            event_type = data['type']
        
        # Handle specific events
        if event_type == 'checkout.session.completed':
            handle_checkout_session_completed(event_data)
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(event_data)
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(event_data)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400