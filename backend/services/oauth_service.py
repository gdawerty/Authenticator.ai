import os
import requests
import secrets
from urllib.parse import urlencode, parse_qs
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class OAuthConfig:
    """OAuth configuration for different providers"""
    
    GOOGLE = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback'),
        'auth_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'scope': 'openid email profile'
    }
    
    MICROSOFT = {
        'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
        'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
        'redirect_uri': os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:5000/auth/microsoft/callback'),
        'auth_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'user_info_url': 'https://graph.microsoft.com/v1.0/me',
        'scope': 'openid email profile User.Read'
    }
    
    GITHUB = {
        'client_id': os.getenv('GITHUB_CLIENT_ID'),
        'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
        'redirect_uri': os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:5000/auth/github/callback'),
        'auth_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'user_info_url': 'https://api.github.com/user',
        'scope': 'user:email'
    }
    
    DISCORD = {
        'client_id': os.getenv('DISCORD_CLIENT_ID'),
        'client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
        'redirect_uri': os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/auth/discord/callback'),
        'auth_url': 'https://discord.com/api/oauth2/authorize',
        'token_url': 'https://discord.com/api/oauth2/token',
        'user_info_url': 'https://discord.com/api/users/@me',
        'scope': 'identify email'
    }

class OAuthService:
    """OAuth service for handling different providers"""
    
    def __init__(self):
        self.state_store = {}  # In production, use Redis or database
    
    def generate_auth_url(self, provider: str) -> Optional[str]:
        """Generate OAuth authorization URL"""
        config = getattr(OAuthConfig, provider.upper(), None)
        if not config or not config['client_id']:
            return None
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        self.state_store[state] = {
            'provider': provider,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=10)
        }
        
        params = {
            'client_id': config['client_id'],
            'redirect_uri': config['redirect_uri'],
            'scope': config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        # Provider-specific parameters
        if provider == 'microsoft':
            params['response_mode'] = 'query'
        
        return f"{config['auth_url']}?{urlencode(params)}"
    
    def verify_state(self, state: str, provider: str) -> bool:
        """Verify OAuth state parameter"""
        if state not in self.state_store:
            return False
        
        stored_state = self.state_store[state]
        if (stored_state['provider'] != provider or 
            datetime.utcnow() > stored_state['expires_at']):
            del self.state_store[state]
            return False
        
        del self.state_store[state]
        return True
    
    def exchange_code_for_token(self, provider: str, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        config = getattr(OAuthConfig, provider.upper(), None)
        if not config:
            return None
        
        data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'code': code,
            'redirect_uri': config['redirect_uri']
        }
        
        # Provider-specific token exchange
        if provider == 'github':
            data['grant_type'] = 'authorization_code'
            headers = {'Accept': 'application/json'}
        else:
            data['grant_type'] = 'authorization_code'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(config['token_url'], data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Token exchange error for {provider}: {e}")
            return None
    
    def get_user_info(self, provider: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from OAuth provider"""
        config = getattr(OAuthConfig, provider.upper(), None)
        if not config:
            return None
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(config['user_info_url'], headers=headers)
            response.raise_for_status()
            user_data = response.json()
            
            # Normalize user data across providers
            return self._normalize_user_data(provider, user_data, access_token)
        except requests.RequestException as e:
            print(f"User info error for {provider}: {e}")
            return None
    
    def _normalize_user_data(self, provider: str, raw_data: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        """Normalize user data from different providers"""
        normalized = {
            'provider': provider,
            'access_token': access_token,
            'raw_data': raw_data
        }
        
        if provider == 'google':
            normalized.update({
                'provider_id': raw_data.get('id'),
                'email': raw_data.get('email'),
                'name': raw_data.get('name'),
                'avatar_url': raw_data.get('picture'),
                'is_verified': raw_data.get('verified_email', False)
            })
        
        elif provider == 'microsoft':
            normalized.update({
                'provider_id': raw_data.get('id'),
                'email': raw_data.get('mail') or raw_data.get('userPrincipalName'),
                'name': raw_data.get('displayName'),
                'avatar_url': None,  # Microsoft Graph API requires separate call
                'is_verified': True  # Microsoft accounts are typically verified
            })
        
        elif provider == 'github':
            # Get email separately for GitHub as it might be private
            email = raw_data.get('email')
            if not email:
                email = self._get_github_primary_email(access_token)
            
            normalized.update({
                'provider_id': str(raw_data.get('id')),
                'email': email,
                'name': raw_data.get('name') or raw_data.get('login'),
                'avatar_url': raw_data.get('avatar_url'),
                'is_verified': True
            })
        
        elif provider == 'discord':
            normalized.update({
                'provider_id': raw_data.get('id'),
                'email': raw_data.get('email'),
                'name': f"{raw_data.get('username')}#{raw_data.get('discriminator')}",
                'avatar_url': self._get_discord_avatar_url(raw_data),
                'is_verified': raw_data.get('verified', False)
            })
        
        return normalized
    
    def _get_github_primary_email(self, access_token: str) -> Optional[str]:
        """Get primary email from GitHub API"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://api.github.com/user/emails', headers=headers)
            response.raise_for_status()
            emails = response.json()
            
            # Find primary email
            for email_info in emails:
                if email_info.get('primary', False):
                    return email_info.get('email')
            
            # Fallback to first email
            if emails:
                return emails[0].get('email')
        except requests.RequestException:
            pass
        return None
    
    def _get_discord_avatar_url(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Generate Discord avatar URL"""
        user_id = user_data.get('id')
        avatar_hash = user_data.get('avatar')
        
        if user_id and avatar_hash:
            return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
        return None

class OAuthManager:
    """Main OAuth manager class"""
    
    def __init__(self):
        self.service = OAuthService()
        self.supported_providers = ['google', 'microsoft', 'github', 'discord']
    
    def get_provider_login_url(self, provider: str) -> Optional[str]:
        """Get login URL for a specific provider"""
        if provider not in self.supported_providers:
            return None
        return self.service.generate_auth_url(provider)
    
    def handle_callback(self, provider: str, code: str, state: str) -> Optional[Dict[str, Any]]:
        """Handle OAuth callback"""
        if provider not in self.supported_providers:
            return None
        
        # Verify state
        if not self.service.verify_state(state, provider):
            return None
        
        # Exchange code for token
        token_data = self.service.exchange_code_for_token(provider, code)
        if not token_data:
            return None
        
        access_token = token_data.get('access_token')
        if not access_token:
            return None
        
        # Get user information
        user_info = self.service.get_user_info(provider, access_token)
        if not user_info:
            return None
        
        # Add token expiration info
        if 'expires_in' in token_data:
            expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
            user_info['token_expires_at'] = expires_at
        
        if 'refresh_token' in token_data:
            user_info['refresh_token'] = token_data['refresh_token']
        
        return user_info
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of configured OAuth providers"""
        providers = []
        for provider in self.supported_providers:
            config = getattr(OAuthConfig, provider.upper(), None)
            if config and config.get('client_id'):
                providers.append({
                    'name': provider,
                    'display_name': provider.title(),
                    'login_url': f'/auth/{provider}'
                })
        return providers

# Global OAuth manager instance
oauth_manager = OAuthManager()
