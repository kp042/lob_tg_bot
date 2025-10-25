import aiohttp
import logging
from typing import Optional, Dict
import asyncio


class APIClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        auth_data = {
            'username': self.username,
            'password': self.password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/token",
                data=auth_data,
                headers={'accept': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.token = result['access_token']
                    logging.info("Successfully authenticated with API")
                    return True
                else:
                    logging.error(f"Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logging.exception(f"Authentication error: {e}")
            return False

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated GET request"""
        if not self.token:
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
                            return await retry_response.json()
                    else:
                        return {"error": "Re-authentication failed"}
                
                return await response.json()
        except Exception as e:
            logging.exception(f"Request error: {e}")
            return {"error": str(e)}

# # Usage in your bot
# async def get_crypto_data():
#     async with APIClient(
#         base_url="http://171.22.79.157:8000",
#         username="your_bot_user",  # Create a dedicated user for the bot
#         password="your_bot_password"
#     ) as api_client:
        
#         # Get available symbols
#         symbols = await api_client.get("/crypto/symbols")
#         print(symbols)
        
#         # Get specific symbol data
#         btc_data = await api_client.get("/crypto/data/BTCUSDT", {"limit": 10})
#         print(btc_data)
