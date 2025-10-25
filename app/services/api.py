import asyncio
import aiohttp
from typing import Dict, List, Optional


async def get_rest(endpoint: str, url: str, params: Optional[Dict] = None) -> Dict:
    session = aiohttp.ClientSession()
    try:
        async with session.get(
            url, 
            params=params, 
            headers={'accept': 'application/json'}
        ) as response:
            return await response.json()
    except Exception as e:
        logging.exception(f"Smth wrong in get_rest request: {e}")
    finally:
        await session.close()

