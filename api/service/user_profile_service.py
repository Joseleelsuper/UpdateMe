import bcrypt
import re
import resend
from flask import jsonify, session
from flask_babel import gettext as _
from api.database import users_collection, db
from api.utils import is_valid_email
from api.service.session_service import invalidate_all_user_sessions

def update_user_profile(user_id, username, email, language='es'):
    """
    Actualiza el perfil del usuario.
    
    Args:
        user_id: ID del usuario
        username: Nuevo nombre de usuario
        email: Nuevo correo electrónico
        language: Idioma preferido
        
    Returns:
        Respuesta JSON con resultado de la operación
    """
    # Validación del nombre de usuario
    if not username or not re.match(r'^[a-zA-Z0-9\s]+$', username):
        return jsonify({
            'success': False,
            'message': _('Username can only contain letters, numbers, and spaces')
        }), 400
    
    # Validación del correo electrónico
    if not is_valid_email(email):
        return jsonify({
            'success': False,
            'message': _('Please enter a valid email address')
        }), 400
    
    # Verificar si el correo electrónico ya existe para otro usuario
    existing_user = users_collection.find_one({'email': email, '_id': {'$ne': user_id}})
    if existing_user:
        return jsonify({
            'success': False,
            'message': _('Email is already in use by another account')
        }), 409
    
    try:
        # Actualizar los datos del usuario
        result = users_collection.update_one(
            {'_id': user_id},
            {'$set': {
                'username': username,
                'email': email,
                'language': language
            }}
        )
        
        if result.modified_count > 0:
            # Actualizar la sesión con los nuevos datos
            session['language'] = language
            
            return jsonify({
                'success': True,
                'message': _('Profile updated successfully')
            })
        else:
            return jsonify({
                'success': False,
                'message': _('No changes were made')
            }), 304
            
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('An unexpected error occurred. Please try again.')
        }), 500

def change_user_password(user_id, current_password, new_password):
    """
    Cambia la contraseña del usuario.
    
    Args:
        user_id: ID del usuario
        current_password: Contraseña actual
        new_password: Nueva contraseña
        
    Returns:
        Respuesta JSON con resultado de la operación
    """
    # Validar requisitos de la nueva contraseña
    if len(new_password) < 6:
        return jsonify({
            'success': False,
            'message': _('Password must be at least 6 characters long')
        }), 400
    
    if not re.search(r'[A-Z]', new_password):
        return jsonify({
            'success': False,
            'message': _('Password must contain at least one uppercase letter')
        }), 400
    
    if not re.search(r'[a-z]', new_password):
        return jsonify({
            'success': False,
            'message': _('Password must contain at least one lowercase letter')
        }), 400
    
    if not re.search(r'[0-9]', new_password):
        return jsonify({
            'success': False,
            'message': _('Password must contain at least one number')
        }), 400
    
    if not re.search(r'[_\W]', new_password):
        return jsonify({
            'success': False,
            'message': _('Password must contain at least one special character')
        }), 400
    
    try:
        # Obtener el usuario actual
        user = users_collection.find_one({'_id': user_id})
        if not user or not user.get('password'):
            return jsonify({
                'success': False,
                'message': _('User not found or no password set')
            }), 404
        
        # Verificar la contraseña actual
        if not bcrypt.checkpw(current_password.encode('utf-8'), 
                             user['password'].encode('utf-8')):

            return jsonify({
                'success': False,
                'message': _('Current password is incorrect')
            }), 401
        
        # Generar hash para la nueva contraseña
        hashed_password = bcrypt.hashpw(
            new_password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Actualizar la contraseña
        result = users_collection.update_one(
            {'_id': user_id},
            {'$set': {'password': hashed_password}}
        )
        
        if result.modified_count > 0:
            # Invalidar todas las sesiones existentes como medida de seguridad
            invalidate_all_user_sessions(user_id)
            
            return jsonify({
                'success': True,
                'message': _('Password changed successfully. Please log in again.')
            })
        else:
            return jsonify({
                'success': False,
                'message': _('No changes were made')
            }), 304
            
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('An unexpected error occurred. Please try again.')
        }), 500

def deactivate_user_account(user_id):
    """
    Desactiva la cuenta del usuario cambiando su estado a 'suspended' y
    lo marca como no suscrito en Resend.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Respuesta JSON con resultado de la operación
    """
    try:
        # Obtener el usuario para conseguir su correo electrónico
        user = users_collection.find_one({'_id': user_id})
        if not user:
            return jsonify({
                'success': False,
                'message': _('User not found')
            }), 404

        # Cambiar el estado de la cuenta a 'suspended'
        result = users_collection.update_one(
            {'_id': user_id},
            {'$set': {'account_status': 'suspended'}}
        )
        
        if result.modified_count > 0:
            # Invalidar todas las sesiones del usuario
            invalidate_all_user_sessions(user_id)
            
            # Actualizar el estado en Resend para desuscribir al usuario
            try:
                # Audience ID de UpdateMe (se debería guardar en una variable de entorno)
                audience_id = "d9811e04-dd4c-4843-8ae4-27d3ac0524e5"
                
                # Configurar los parámetros para actualizar el contacto
                resend_params = {
                    "email": user['email'],
                    "audience_id": audience_id,
                    "unsubscribed": True
                }
                
                # Actualizar el estado del contacto en Resend
                resend.Contacts.update(resend_params)
                
                print(f"Usuario {user['email']} desuscrito de Resend exitosamente")
                
            except Exception as resend_error:
                # Solo registrar el error, no fallamos la operación principal
                print(f"Error actualizando estado en Resend: {str(resend_error)}")
            
            return jsonify({
                'success': True,
                'message': _('Your account has been deactivated. You will no longer receive emails from us.')
            })
        else:
            return jsonify({
                'success': False,
                'message': _('No changes were made')
            }), 304
            
    except Exception as e:
        print(f"Error deactivating account: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('An unexpected error occurred. Please try again.')
        }), 500

def reactivate_user_account(user_id):
    """
    Reactiva una cuenta de usuario suspendida cambiando su estado a 'active'
    y actualizando su estado en Resend para permitir el envío de emails.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Respuesta JSON con resultado de la operación
    """
    try:
        # Obtener el usuario para conseguir su correo electrónico
        user = users_collection.find_one({'_id': user_id})
        if not user:
            return jsonify({
                'success': False,
                'message': _('User not found')
            }), 404

        # Comprobar si la cuenta ya está activa
        if user.get('account_status') == 'active':
            return jsonify({
                'success': False,
                'message': _('Account is already active')
            }), 400

        # Cambiar el estado de la cuenta a 'active'
        result = users_collection.update_one(
            {'_id': user_id},
            {'$set': {'account_status': 'active'}}
        )
        
        if result.modified_count > 0:
            # Actualizar el estado en Resend para suscribir nuevamente al usuario
            try:
                # Audience ID de UpdateMe (se debería guardar en una variable de entorno)
                audience_id = "d9811e04-dd4c-4843-8ae4-27d3ac0524e5"
                
                # Configurar los parámetros para actualizar el contacto
                resend_params = {
                    "email": user['email'],
                    "audience_id": audience_id,
                    "unsubscribed": False  # Suscribir nuevamente al usuario
                }
                
                # Actualizar el estado del contacto en Resend
                resend.Contacts.update(resend_params)
                
                print(f"Usuario {user['email']} suscrito nuevamente en Resend exitosamente")
                
            except Exception as resend_error:
                # Solo registrar el error, no fallamos la operación principal
                print(f"Error actualizando estado en Resend: {str(resend_error)}")
            
            return jsonify({
                'success': True,
                'message': _('Your account has been reactivated successfully. You will start receiving emails again.')
            })
        else:
            return jsonify({
                'success': False,
                'message': _('No changes were made')
            }), 304
            
    except Exception as e:
        print(f"Error reactivating account: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('An unexpected error occurred. Please try again.')
        }), 500

def delete_user_account(user_id):
    """
    Elimina permanentemente la cuenta del usuario y todos sus datos asociados.
    También lo marca como no suscrito en Resend.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Respuesta JSON con resultado de la operación
    """
    try:
        # Obtener información del usuario antes de eliminarlo
        user = users_collection.find_one({'_id': user_id})
        if not user:
            return jsonify({
                'success': False,
                'message': _('User not found')
            }), 404
        
        # Guardar el email antes de eliminar el usuario
        user_email = user.get('email')
        
        # Eliminar documentos asociados
        prompts_id = user.get('prompts')
        if prompts_id:
            db.prompts.delete_one({'_id': prompts_id})
        
        # Eliminar sesiones del usuario
        db.sessions.delete_many({'user_id': user_id})
        
        # Eliminar cliente de Stripe si existe
        if user.get('stripe_customer_id'):
            db.stripe_customers.delete_one({'_id': user.get('stripe_customer_id')})
        
        # Finalmente, eliminar el usuario
        result = users_collection.delete_one({'_id': user_id})
        
        if result.deleted_count > 0:
            # Limpiar la sesión actual
            session.clear()
            
            # Actualizar el estado en Resend para desuscribir al usuario
            try:
                # Audience ID de UpdateMe (se debería guardar en una variable de entorno)
                audience_id = "d9811e04-dd4c-4843-8ae4-27d3ac0524e5"
                
                # Configurar los parámetros para actualizar el contacto
                resend_params = {
                    "email": user_email,
                    "audience_id": audience_id,
                    "unsubscribed": True
                }
                
                # Actualizar el estado del contacto en Resend
                resend.Contacts.update(resend_params)
                
                print(f"Usuario {user_email} desuscrito de Resend exitosamente")
                
            except Exception as resend_error:
                # Solo registrar el error, no fallamos la operación principal
                print(f"Error actualizando estado en Resend: {str(resend_error)}")
            
            return jsonify({
                'success': True,
                'message': _('Your account and all associated data have been permanently deleted.')
            })
        else:
            return jsonify({
                'success': False,
                'message': _('Failed to delete account')
            }), 500
            
    except Exception as e:
        print(f"Error deleting account: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('An unexpected error occurred. Please try again.')
        }), 500