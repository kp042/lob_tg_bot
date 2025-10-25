import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.app_context import app_context
from services.lob_data import get_active_symbols, get_lob_depth
from services.utils import split_list_into_strings

class FSMParameters(StatesGroup):
    waiting_for_ticker = State()
    


router = Router()


@router.message(Command(commands="symbols"))
async def process_symbols(message: Message):
    app_context.symbols = await get_active_symbols()
    msgs = split_list_into_strings(app_context.symbols)
    for msg in msgs:
        await message.answer(msg)


@router.message(Command(commands="check_lob_by_symbol"))
async def process_check_lob_by_symbol(message: Message, state: FSMContext):
    app_context.symbols = await get_active_symbols()
    await message.answer("Input ticker")
    await state.set_state(FSMParameters.waiting_for_ticker)


@router.message(StateFilter(FSMParameters.waiting_for_ticker),
                F.text.upper().in_(app_context.symbols))
async def process_check_lob_by_symbol2(message: Message, state: FSMContext):
    await state.clear()
    symbol = str(message.text)
    logging.debug(f"symbol accepted: {symbol}")

    data = await get_lob_depth(symbol.upper())

    await message.answer(f"Len:{len(data)}")
    for pct in [1, 3, 5, 8]:
        img_filename, desc = make_chart_depth(data, pct, 0)
        await send_image(message.chat.id, img_filename, desc)
        await asyncio.sleep(0.5)


