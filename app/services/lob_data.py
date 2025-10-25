import asyncio
import requests
import aiohttp
import logging
import pandas as pd
from typing import Dict, Optional
from services.utils import get_depths
from core.config import config
from core.app_context import app_context


async def get_lob_depth(symbol: str):
    endpoint = f"/crypto/data/{symbol}"

    async with app_context.api_client as client:
        result = await client.get("/crypto/symbols")
        
    df = pd.DataFrame(result['data'])

    # Обрабатываем разные форматы временных меток
    def parse_timestamp(ts):
        try:
            # Пробуем парсить с миллисекундами
            return pd.to_datetime(ts, format='%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            try:
                # Пробуем парсить без миллисекунд
                return pd.to_datetime(ts, format='%Y-%m-%dT%H:%M:%S')
            except ValueError:
                # Если оба варианта не работают, используем автоматическое определение
                return pd.to_datetime(ts)
    
    df['event_time'] = df['event_time'].apply(parse_timestamp)
    df['event_time'] = df['event_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

async def get_active_symbols():
    async with app_context.api_client as client:
        result = await client.get("/crypto/symbols")
        if 'error' not in result:
            return result
        else:
            logging.warning(f"smth wrong in get_active_symbols: {result}")
