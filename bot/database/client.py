from supabase import create_client, Client
import config
from utils.logger import logger

supabase: Client = create_client(
    config.SUPABASE_URL,
    config.SUPABASE_SERVICE_ROLE_KEY,
)

logger.info("Supabase client initialized")
