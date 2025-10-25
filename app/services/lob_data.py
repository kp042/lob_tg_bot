import pandas as pd
import logging
from typing import Optional
from core.app_context import app_context


async def get_lob_depth(symbol: str, limit: int = 1000):
    """Get LOB depth data for symbol"""
    endpoint = f"/crypto/data/{symbol.upper()}"
    params = {"limit": limit}
    
    result = await app_context.api_client.get(endpoint, params=params)
    
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Error getting LOB data for {symbol}: {result['error']}")
        return None
    
    if isinstance(result, dict) and 'data' in result:
        data = result['data']
    elif isinstance(result, list):
        data = result
    else:
        logging.error(f"Unexpected response format: {type(result)}")
        return None
    
    if not data:
        logging.warning(f"No data returned for symbol {symbol}")
        return None
    
    try:
        df = pd.DataFrame(data)
        
        # Convert UNIX timestamp to datetime - FIXED for FutureWarning
        if 'event_time' in df.columns:
            # First convert to numeric to handle string timestamps
            df['event_time'] = pd.to_numeric(df['event_time'], errors='coerce')
            # Then convert to datetime
            df['event_time'] = pd.to_datetime(df['event_time'], unit='s')
        
        # Convert depth columns to numeric
        depth_columns = [col for col in df.columns if 'depth' in col]
        for col in depth_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert other numeric columns
        numeric_columns = ['best_bid', 'best_ask', 'min_bid', 'max_ask']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sort by timestamp if available
        if 'event_time' in df.columns:
            df = df.sort_values('event_time').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        logging.exception(f"Error processing LOB data: {e}")
        return None


async def get_active_symbols() -> list:
    """Get list of active symbols"""
    result = await app_context.api_client.get("/crypto/symbols")

    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and 'error' in result:
        logging.error(f"API error: {result['error']}")
        return []
    else:
        logging.error(f"Unexpected response format: {type(result)} - {result}")
        return []
    
