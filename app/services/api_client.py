import aiohttp
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta


class APIClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = None
        self.session = None

    async def ensure_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
            await self.authenticate()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        auth_data = {
            'username': self.username,
            'password': self.password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/token",
                data=aiohttp.FormData(auth_data),
                headers={'accept': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.token = result['access_token']
                    # Предполагаем, что токен живет 30 минут
                    self.token_expiry = datetime.now() + timedelta(minutes=30)
                    logging.info("Successfully authenticated with API")
                    return True
                else:
                    logging.error(f"Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logging.exception(f"Authentication error: {e}")
            return False

    async def is_token_valid(self) -> bool:
        """Check if token is still valid"""
        return self.token and self.token_expiry and datetime.now() < self.token_expiry

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated GET request"""
        await self.ensure_session()
        
        if not await self.is_token_valid():
            if not await self.authenticate():
                return {"error": "Authentication failed"}

        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.get(
                url, 
                params=params, 
                headers=headers
            ) as response:
                if response.status == 401:  # Token expired
                    logging.info("Token expired, re-authenticating...")
                    if await self.authenticate():
                        # Retry with new token
                        headers['Authorization'] = f'Bearer {self.token}'
                        async with self.session.get(
                            url, params=params, headers=headers
                        ) as retry_response:
                            return await self._handle_response(retry_response)
                    else:
                        return {"error": "Re-authentication failed"}
                
                return await self._handle_response(response)
        except Exception as e:
            logging.exception(f"Request error: {e}")
            return {"error": str(e)}

    async def _handle_response(self, response):
        """Handle API response"""
        if response.status == 200:
            return await response.json()
        else:
            error_text = await response.text()
            logging.error(f"API error {response.status}: {error_text}")
            return {"error": f"HTTP {response.status}: {error_text}"}
