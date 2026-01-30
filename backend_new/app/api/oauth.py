from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
from urllib.parse import urlencode
import secrets

from app.core.config import settings
from app.db.session import get_db
from app.models.db_models import UserModel
from app.api.auth import create_access_token

router = APIRouter()

# Store OAuth states temporarily (in production, use Redis or database)
oauth_states = {}


@router.get("/login/{provider}")
async def oauth_login(provider: str):
    """
    Initiate OAuth login with the specified provider

    Args:
        provider: OAuth provider (google, github, microsoft)
    """
    if provider not in ['google', 'github', 'microsoft']:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = provider

    redirect_uri = f"http://localhost:8002/api/v1/oauth/callback/{provider}"

    if provider == 'google':
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    elif provider == 'github':
        params = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'user:email',
            'state': state
        }
        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    elif provider == 'microsoft':
        params = {
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state
        }
        auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"

    return RedirectResponse(url=auth_url)


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str,
    state: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from the provider

    Args:
        provider: OAuth provider (google, github, microsoft)
        code: Authorization code from provider
        state: State parameter for CSRF protection
    """
    try:
        # Verify state
        if state and state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        redirect_uri = f"http://localhost:8002/api/v1/oauth/callback/{provider}"

        async with httpx.AsyncClient() as client:
            # Exchange code for token
            if provider == 'google':
                token_response = await client.post(
                    'https://oauth2.googleapis.com/token',
                    data={
                        'code': code,
                        'client_id': settings.GOOGLE_CLIENT_ID,
                        'client_secret': settings.GOOGLE_CLIENT_SECRET,
                        'redirect_uri': redirect_uri,
                        'grant_type': 'authorization_code'
                    }
                )
                token_data = token_response.json()
                access_token = token_data.get('access_token')

                # Get user info
                user_response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info = user_response.json()
                email = user_info.get('email')
                name = user_info.get('name')
                profile_picture = user_info.get('picture')

            elif provider == 'github':
                token_response = await client.post(
                    'https://github.com/login/oauth/access_token',
                    data={
                        'code': code,
                        'client_id': settings.GITHUB_CLIENT_ID,
                        'client_secret': settings.GITHUB_CLIENT_SECRET,
                        'redirect_uri': redirect_uri
                    },
                    headers={'Accept': 'application/json'}
                )
                token_data = token_response.json()
                access_token = token_data.get('access_token')

                # Get user info
                user_response = await client.get(
                    'https://api.github.com/user',
                    headers={'Authorization': f'token {access_token}'}
                )
                user_info = user_response.json()

                # Get primary email
                email_response = await client.get(
                    'https://api.github.com/user/emails',
                    headers={'Authorization': f'token {access_token}'}
                )
                emails = email_response.json()
                email = next((e['email'] for e in emails if e.get('primary')), emails[0]['email'] if emails else None)
                name = user_info.get('name') or user_info.get('login')
                profile_picture = user_info.get('avatar_url')

            elif provider == 'microsoft':
                token_response = await client.post(
                    'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                    data={
                        'code': code,
                        'client_id': settings.MICROSOFT_CLIENT_ID,
                        'client_secret': settings.MICROSOFT_CLIENT_SECRET,
                        'redirect_uri': redirect_uri,
                        'grant_type': 'authorization_code',
                        'scope': 'openid email profile'
                    }
                )
                token_data = token_response.json()
                access_token = token_data.get('access_token')

                # Get user info
                user_response = await client.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info = user_response.json()
                email = user_info.get('mail') or user_info.get('userPrincipalName')
                name = user_info.get('displayName')
                # Microsoft doesn't have a simple URL for profile picture, we'd need to fetch it separately
                # For now, we'll leave it as None for Microsoft users
                profile_picture = None

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

            if not email:
                raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

            # Check if user exists
            user = db.query(UserModel).filter(UserModel.email == email).first()

            if not user:
                # Create new user
                user = UserModel(
                    email=email,
                    username=name or email.split('@')[0],
                    hashed_password=None,  # OAuth users don't have passwords
                    oauth_provider=provider,
                    profile_picture=profile_picture
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update profile picture if it changed
                if profile_picture and user.profile_picture != profile_picture:
                    user.profile_picture = profile_picture
                    db.commit()
                    db.refresh(user)

            # Create access token (use user.id for consistency with regular login)
            access_token = create_access_token(data={"sub": str(user.id)})

            # Clean up state
            if state in oauth_states:
                del oauth_states[state]

            # Redirect to frontend with token
            return RedirectResponse(
                url=f"http://localhost:5175/auth/success?token={access_token}&provider={provider}"
            )

    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")


@router.get("/providers")
async def get_oauth_providers():
    """
    Get list of configured OAuth providers
    """
    providers = []

    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_ID != 'your-google-client-id':
        providers.append({
            'name': 'google',
            'display_name': 'Google',
            'icon': '🔵'
        })

    if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_ID != 'your-github-client-id':
        providers.append({
            'name': 'github',
            'display_name': 'GitHub',
            'icon': '⚫'
        })

    if settings.MICROSOFT_CLIENT_ID and settings.MICROSOFT_CLIENT_ID != 'your-microsoft-client-id':
        providers.append({
            'name': 'microsoft',
            'display_name': 'Microsoft',
            'icon': '🟦'
        })

    return {'providers': providers}
