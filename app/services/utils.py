import pandas as pd
import matplotlib.pyplot as plt
from typing import Literal
import os
import logging


DepthType = Literal[1, 3, 5, 8]
depths = {
    1: ["depth_1pct_bid", "depth_1pct_ask"],
    3: ["depth_3pct_bid", "depth_3pct_ask"],
    5: ["depth_5pct_bid", "depth_5pct_ask"],
    8: ["depth_8pct_bid", "depth_8pct_ask"]
}


def get_depths(depth_type: DepthType) -> list[str]:
    if depth_type not in depths:
        raise ValueError(f"Invalid depth_type: {depth_type}. Must be one of {list(depths.keys())}")
    return depths[depth_type]


def split_list_into_strings(lst, max_length=4000, separator=', '):
    """
    Split list into multiple strings without exceeding max_length
    """
    if not lst:
        return []
    
    results = []
    current_chunk = []
    current_length = 0
    
    for item in lst:
        item_str = str(item)
        item_length = len(item_str)
        
        # Calculate new length including separator if not first item
        if current_chunk:
            new_length = current_length + len(separator) + item_length
        else:
            new_length = item_length
        
        # If adding this item would exceed limit, save current chunk and start new one
        if new_length > max_length:
            if current_chunk:
                chunk_text = separator.join(current_chunk)
                results.append(chunk_text)
                logging.debug(f"Created chunk with length {len(chunk_text)}")
                current_chunk = [item_str]
                current_length = item_length
            else:
                # Single item is too long, truncate it
                truncated = item_str[:max_length]
                results.append(truncated)
                logging.warning(f"Truncated long item: {item_str}")
                current_chunk = []
                current_length = 0
        else:
            current_chunk.append(item_str)
            current_length = new_length
    
    # Add the last chunk if not empty
    if current_chunk:
        chunk_text = separator.join(current_chunk)
        results.append(chunk_text)
        logging.debug(f"Created final chunk with length {len(chunk_text)}")
    
    logging.info(f"Split {len(lst)} items into {len(results)} chunks")
    return results

# def split_list_into_strings(lst, max_length=4095, separator=', '):
#     results = []
#     current_string = ''
#     for element in lst:
#         if current_string:
#             next_string = current_string + separator + element
#         else:
#             next_string = element
#         if len(next_string) > max_length:
#             if current_string:
#                 results.append(current_string)
#             current_string = element
#             if len(element) > max_length:                
#                 pass
#         else:
#             current_string = next_string
#     if current_string:
#         results.append(current_string)
#     return results


def make_chart_depth(df: pd.DataFrame, pct: int, depth_type: int):
    """
    Generate depth chart
    
    Args:
        df: DataFrame with LOB data
        pct: depth percent (1, 3, 5, 8)
        depth_type: chart type (0 - bids/asks, 1 - k bids/asks, 2 - difference %)
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Use event_time as timestamp
    if 'event_time' not in df.columns:
        raise ValueError("DataFrame must contain 'event_time' column")
    
    df_sorted = df.sort_values('event_time').reset_index(drop=True)
    
    # Chart setup
    width_px, height_px = 500, 900
    filename = os.path.join(os.path.dirname(__file__), "output_graph.png")
    dpi = 100
    
    # Suppress matplotlib debug messages
    plt.ioff()  # Turn off interactive mode
    plt.style.use('dark_background')
    
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width_px/dpi, height_px/dpi), 
                                       sharex=True, dpi=dpi)

        # Top plot: best bid/ask
        ax1.plot(df_sorted['event_time'], df_sorted['best_bid'], 
                 color='green', label='Best Bid', linewidth=1)
        ax1.plot(df_sorted['event_time'], df_sorted['best_ask'], 
                 color='red', label='Best Ask', linewidth=1)
        ax1.set_ylabel('Price', color='white')
        ax1.legend()
        ax1.tick_params(axis='y', colors='white')
        ax1.grid(True, linestyle='--', alpha=0.3, color='gray')

        depth_lst = get_depths(pct)
        description = ""

        # Bottom plot based on depth type
        if depth_type == 0:
            description = f"Depth ({pct}% Bid/Ask)"
            ax2.plot(df_sorted['event_time'], df_sorted[depth_lst[0]], 
                    color='lightgreen', label=f'Bid {pct}%', linewidth=1)
            ax2.plot(df_sorted['event_time'], df_sorted[depth_lst[1]], 
                    color='lightcoral', label=f'Ask {pct}%', linewidth=1)
            ax2.set_ylabel('Volume', color='white')
            ax2.legend()
        elif depth_type == 1:
            description = f"Depth ({pct}% K Bid/Ask)"
            if all(col in df_sorted.columns for col in depth_lst):
                df_sorted['k_ratio'] = (pd.to_numeric(df_sorted[depth_lst[0]], errors='coerce') / 
                                      pd.to_numeric(df_sorted[depth_lst[1]], errors='coerce'))
                ax2.plot(df_sorted['event_time'], df_sorted['k_ratio'], 
                        color='blue', label='Bid/Ask Ratio', linewidth=1)
                ax2.set_ylabel('Ratio', color='white')
                ax2.legend()
        elif depth_type == 2:
            description = f"Depth ({pct}% diff % Bids-Asks)"
            if all(col in df_sorted.columns for col in depth_lst):
                bid_vol = pd.to_numeric(df_sorted[depth_lst[0]], errors='coerce')
                ask_vol = pd.to_numeric(df_sorted[depth_lst[1]], errors='coerce')
                df_sorted['diff_pct'] = (bid_vol - ask_vol) / (bid_vol + ask_vol) * 100
                ax2.plot(df_sorted['event_time'], df_sorted['diff_pct'], 
                        color='cyan', label='Bid-Ask Diff %', linewidth=1)
                ax2.set_ylabel('Difference %', color='white')
                ax2.legend()
        
        ax2.tick_params(axis='y', colors='white')
        ax2.grid(True, linestyle='--', alpha=0.3, color='gray')

        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot
        plt.savefig(filename, dpi=dpi, bbox_inches='tight', 
                    facecolor='#1a1a1a', edgecolor='none')
        
        logging.info(f"Chart saved: {filename}")
        return filename, description
        
    finally:
        # Ensure proper cleanup even if there's an error
        plt.close(fig)
        plt.close('all')
    

