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


def split_list_into_strings(lst, max_length=4095, separator=', '):
    results = []
    current_string = ''
    for element in lst:
        if current_string:
            next_string = current_string + separator + element
        else:
            next_string = element
        if len(next_string) > max_length:
            if current_string:
                results.append(current_string)
            current_string = element
            if len(element) > max_length:
                # Если отдельный элемент длиннее max_length,
                # его можно обработать отдельно или всё равно добавить
                pass
        else:
            current_string = next_string
    if current_string:
        results.append(current_string)
    return results


def make_chart_depth(df: pd.DataFrame, pct: int, depth_type: int):
    """
    df - dataframe
    pct - depth percent
    depth_type - chart type depends on depth visualisation (0 - bids/asks, 1 - k bids/asks, 2 - difference %)
    
    
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    
    width_px = 500  # Ширина в пикселях
    height_px = 900  # Высота в пикселях

    # filename = "output_graph.png"  # Имя файла для сохранения
    filename = os.path.join(os.path.dirname(__file__), "output_graph.png")

    dpi = 100  # Разрешение (DPI)
    # Переводим пиксели в дюймы (1 дюйм = dpi пикселей)
    fig_width = width_px / dpi
    fig_height = height_px / dpi

    # Темный фон
    plt.style.use('dark_background')
    # Создаем фигуру с заданными размерами
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(fig_width, fig_height), sharex=True, dpi=dpi)

    # Верхний график: best_bid
    ax1.plot(df['timestamp'], df['best_bid'], color='white')  # Без маркеров
    ax1.set_ylabel('Best Bid', color='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.grid(True, linestyle='--', alpha=0.3, color='gray')

    depth_lst = get_depths(pct)

    description = ""

    # Нижний график: 
    if depth_type == 0:
        description = f"Depth ({pct}% Bid/Ask)"
        ax2.plot(df['timestamp'], df[depth_lst[0]], color='green')  # Без маркеров
        ax2.plot(df['timestamp'], df[depth_lst[1]], color='red')
        ax2.set_ylabel(description, color='white')
    elif depth_type == 1:
        description = f"Depth ({pct}% K Bid/Ask)"
        ax2.plot(df['timestamp'], df['k'], color='blue')
        ax2.set_ylabel(description, color='white')
    elif depth_type == 2:
        description = f"Depth ({pct}% diff % Bids-Asks)"
        df['diff'] = (df[depth_lst[1]] - df[depth_lst[0]])/(df[depth_lst[0]] + df[depth_lst[1]]) * 100
        ax2.plot(df['timestamp'], df['diff'], color='cyan')
        ax2.set_ylabel(description, color='white')
    
    ax2.tick_params(axis='y', colors='white')
    ax2.grid(True, linestyle='--', alpha=0.3, color='gray')

    # Скрываем метки времени на оси X
    ax1.xaxis.set_visible(False)
    ax2.xaxis.set_visible(False)

    # Убираем промежутки между графиками
    plt.tight_layout()

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, hspace=0.01)

    # Сохраняем график в файл
    plt.savefig(filename, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    plt.close('all')
    logging.info(f"Saving image to: {os.path.abspath(filename)}")

    return filename, description
    

