import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


def clean_supabase_url(url: str) -> str:
    """Strips trailing slashes and /rest/v1 if included."""
    cleaned = (url or "").strip().rstrip("/")
    if cleaned.endswith("/rest/v1"):
        cleaned = cleaned[:-8].rstrip("/")
    return cleaned


def is_supabase_configured() -> bool:
    """Check if Supabase credentials are validly configured."""
    url = clean_supabase_url(settings.SUPABASE_URL)
    return bool(
        url
        and settings.SUPABASE_KEY
        and url.startswith("http")
        and not url.startswith("https://your-project")
    )


def init_supabase() -> Optional[Client]:
    """Initialize and return the reusable Supabase client instance."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if is_supabase_configured():
        try:
            url = clean_supabase_url(settings.SUPABASE_URL)
            _supabase_client = create_client(url, settings.SUPABASE_KEY.strip())
            logger.info("Supabase client initialized successfully with project URL: %s", url)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            _supabase_client = None
    else:
        logger.warning(
            "Supabase credentials not configured in .env. Running with local in-memory fallback store."
        )
    return _supabase_client


# Initialize reusable client
supabase: Optional[Client] = init_supabase()


def get_supabase() -> Optional[Client]:
    """Get the current reusable Supabase client instance."""
    global _supabase_client
    if _supabase_client is None and is_supabase_configured():
        _supabase_client = init_supabase()
    return _supabase_client


def get_authenticated_client(token: Optional[str] = None) -> Optional[Client]:
    """Returns a client with user token attached to PostgREST for RLS compliance."""
    client = get_supabase()
    if client and token:
        try:
            client.postgrest.auth(token)
        except Exception as e:
            logger.debug(f"Unable to attach token to postgrest: {e}")
    return client
