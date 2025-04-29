from flask import Blueprint, request, jsonify, g
from flask_babel import gettext as _
from api.auth import login_required
from api.service.user_profile_service import (
    update_user_profile,
    change_user_password,
    deactivate_user_account,
    reactivate_user_account,
    delete_user_account
)

# Crear el blueprint para las rutas de perfil de usuario
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    """
    Renderiza la página de perfil del usuario.
    """
    from flask import render_template, url_for
    
    title = _('UpdateMe - My Profile')
    # Metadatos SEO para la página de perfil
    meta = {
        'meta_description': _('Manage your UpdateMe account settings and subscription preferences.'),
        'meta_keywords': 'profile, account settings, user preferences',
        'canonical_url': url_for('main.profile.profile', _external=True),
        'meta_robots': 'noindex, nofollow'  # Páginas de usuario no deberían indexarse
    }
    return render_template('profile.html', title=title, user=g.user, **meta)

@profile_bp.route('/api/user/profile', methods=['POST'])
@login_required
def update_profile():
    """
    Actualiza los datos del perfil del usuario.
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    language = data.get('language', 'es')
    
    # Validación básica
    if not username:
        return jsonify({
            'success': False,
            'message': _('Username cannot be empty')
        }), 400
    
    if not email:
        return jsonify({
            'success': False,
            'message': _('Email cannot be empty')
        }), 400
    
    # Llamar al servicio para actualizar el perfil
    return update_user_profile(g.user['_id'], username, email, language)

@profile_bp.route('/api/user/password', methods=['POST'])
@login_required
def update_password():
    """
    Actualiza la contraseña del usuario.
    """
    data = request.get_json()
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    
    # Validación básica
    if not current_password or not new_password:
        return jsonify({
            'success': False,
            'message': _('Both current and new password are required')
        }), 400
    
    # Llamar al servicio para cambiar la contraseña
    return change_user_password(g.user['_id'], current_password, new_password)

@profile_bp.route('/api/user/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    """
    Desactiva la cuenta del usuario (cambia estado a 'suspended').
    """
    # Llamar al servicio para desactivar la cuenta
    return deactivate_user_account(g.user['_id'])

@profile_bp.route('/api/user/reactivate', methods=['POST'])
@login_required
def reactivate_account():
    """
    Reactiva una cuenta de usuario suspendida (cambia estado a 'active').
    """
    # Llamar al servicio para reactivar la cuenta
    return reactivate_user_account(g.user['_id'])

@profile_bp.route('/api/user/delete', methods=['DELETE'])
@login_required
def delete_account():
    """
    Elimina permanentemente la cuenta del usuario y todos sus datos.
    """
    # Llamar al servicio para eliminar la cuenta
    return delete_user_account(g.user['_id'])