import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.app_context import app_context
from services.lob_data import get_active_symbols, get_lob_depth
from services.utils import make_chart_depth
from services.msg_manager import send_image


class FSMParameters(StatesGroup):
    waiting_for_ticker = State()


router = Router()

# symbols
@router.message(Command(commands="symbols"))
async def process_symbols(message: Message):
    symbols = await get_active_symbols()
    
    if not symbols:
        await message.answer("❌ No symbols available or error fetching symbols")
        return
    
    # Store in app context for later use
    app_context.symbols = symbols
    
    await message.answer(f"📊 Found {len(symbols)} active symbols")
    
    # Split long lists to avoid message limits - use more conservative approach
    from services.utils import split_list_into_strings
    msgs = split_list_into_strings(symbols, max_length=3500)  # Reduced for safety
    
    for i, msg in enumerate(msgs, 1):
        try:
            # Create message with length check
            message_text = f"Symbols (part {i}/{len(msgs)}):\n{msg}"
            
            # Double-check length before sending
            if len(message_text) > 4096:
                logging.warning(f"Message part {i} still too long: {len(message_text)}")
                # Emergency split - send without header
                emergency_msgs = split_list_into_strings([msg], max_length=4000)
                for j, emergency_msg in enumerate(emergency_msgs, 1):
                    await message.answer(f"Symbols continuation...\n{emergency_msg}")
                    await asyncio.sleep(0.1)
            else:
                await message.answer(message_text)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logging.error(f"Error sending symbols part {i}: {e}")
            # Try sending without header as fallback
            try:
                emergency_msgs = split_list_into_strings([msg], max_length=4000)
                for emergency_msg in emergency_msgs:
                    await message.answer(emergency_msg)
                    await asyncio.sleep(0.1)
            except Exception as e2:
                logging.error(f"Even fallback failed: {e2}")


# check_lob_by_symbol
@router.message(Command(commands="check_lob_by_symbol"))
async def process_check_lob_by_symbol(message: Message, state: FSMContext):
    symbols = await get_active_symbols()
    if not symbols:
        await message.answer("Error: Could not fetch available symbols")
        return
        
    app_context.symbols = symbols
    await message.answer("Input ticker (e.g., BTCUSDT, ETHUSDT):")
    await state.set_state(FSMParameters.waiting_for_ticker)

@router.message(StateFilter(FSMParameters.waiting_for_ticker))
async def process_ticker_input(message: Message, state: FSMContext):
    symbol = message.text.upper().strip()
    
    # Validate symbol
    if symbol not in app_context.symbols:
        await message.answer(f"Symbol '{symbol}' not found. Please enter a valid symbol.")
        return
    
    await state.clear()
    await message.answer(f"Fetching LOB data for {symbol}...")
    
    try:
        # Get LOB data
        data = await get_lob_depth(symbol, limit=1000)
        
        if data is None or data.empty:
            await message.answer(f"No data available for {symbol}")
            return
            
        await message.answer(f"Retrieved {len(data)} records for {symbol}")
        
        # Generate and send charts for different depths 1%, 3%, 5%, 8%
        for pct in [1, 3, 5, 8]:
            try:
                img_filename, desc = make_chart_depth(data, pct, 0)
                await send_image(message.chat.id, img_filename, f"{symbol} - {desc}")
                await asyncio.sleep(0.5)  # Small delay between messages
            except Exception as e:
                logging.error(f"Error generating chart for {symbol} at {pct}%: {e}")
                await message.answer(f"Error generating chart for {pct}% depth")
                
    except Exception as e:
        logging.exception(f"Error processing LOB data for {symbol}")
        await message.answer(f"Error processing data for {symbol}: {str(e)}")
