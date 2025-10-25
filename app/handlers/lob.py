import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



class FSMParameters(StatesGroup):
    waiting_for_ticker = State()
    


router = Router()


@router.message(Command(commands="b8s_history_depths"))
async def process_b8s_history_depths(message: Message, state: FSMContext):
    settings.update_b8sdepth_tickers()
    await message.answer("Input ticker")
    await state.set_state(FSMParameters.waiting_for_ticker)


@router.message(StateFilter(FSMParameters.waiting_for_ticker),
                F.text.upper().in_(settings.b8sdepth_tickers))
async def process_b8s_history_depths2(message: Message, state: FSMContext):
    await state.clear()    
    symbol = str(message.text)
    logging.info(f"ticker accepted: {symbol}")
    data = await get_history_depth(symbol.upper())
    await message.answer(f"Len:{len(data)}")
    for pct in [1, 3, 5, 8]:
        img_filename, desc = make_chart_depth(data, pct, 0)
        await send_image(message.chat.id, img_filename, desc)
        await asyncio.sleep(0.5)


