import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
Message,
ReplyKeyboardMarkup,
KeyboardButton,
InlineKeyboardMarkup,
InlineKeyboardButton,
CallbackQuery
)

TOKEN = os.getenv("8742073683:AAGL64E4ulGAiXCmlXefRhh6jWdFxx86sLM")

ADMIN_ID = 5541045710

CARD_NUMBER = "6219-8618-6362-3830"
CARD_OWNER = "علیرضا محبی"

logging.basicConfig(level=logging.INFO)

bot = Bot(
token=TOKEN,
parse_mode=ParseMode.HTML
)

dp = Dispatcher()

pending_users = {}

main_menu = ReplyKeyboardMarkup(
keyboard=[
[KeyboardButton(text="🔥 خرید سرویس حرفه ای")],
[KeyboardButton(text="💎 خرید سرویس اقتصادی")]
],
resize_keyboard=True
)

pro_plans = InlineKeyboardMarkup(
inline_keyboard=[
[InlineKeyboardButton(text="1GB - 360.000", callback_data="plan_pro_1GB_360000")],
[InlineKeyboardButton(text="5GB - 1.690.000", callback_data="plan_pro_5GB_1690000")],
[InlineKeyboardButton(text="10GB - 3.400.000", callback_data="plan_pro_10GB_3400000")],
[InlineKeyboardButton(text="20GB - 5.200.000", callback_data="plan_pro_20GB_5200000")],
[InlineKeyboardButton(text="50GB - 11.200.000", callback_data="plan_pro_50GB_11200000")]
]
)

eco_plans = InlineKeyboardMarkup(
inline_keyboard=[
[InlineKeyboardButton(text="10GB - 2.500.000", callback_data="plan_eco_10GB_2500000")],
[InlineKeyboardButton(text="20GB - 3.900.000", callback_data="plan_eco_20GB_3900000")],
[InlineKeyboardButton(text="40GB - 7.000.000", callback_data="plan_eco_40GB_7000000")]
]
)

@dp.message(CommandStart())
async def start(message: Message):

```
text = f"""
```

👋 سلام {message.from_user.first_name}

به فروشگاه VPN خوش اومدی 🚀

لطفا نوع سرویس مورد نظر رو انتخاب کن:
"""

```
await message.answer(
    text,
    reply_markup=main_menu
)
```

@dp.message(F.text == "🔥 خرید سرویس حرفه ای")
async def pro_service(message: Message):

```
await message.answer(
    "🔥 لیست سرویس های حرفه ای:",
    reply_markup=pro_plans
)
```

@dp.message(F.text == "💎 خرید سرویس اقتصادی")
async def eco_service(message: Message):

```
await message.answer(
    "💎 لیست سرویس های اقتصادی:",
    reply_markup=eco_plans
)
```

@dp.callback_query(F.data.startswith("plan_"))
async def select_plan(callback: CallbackQuery):

```
data = callback.data.split("_")

category = data[1]
volume = data[2]
price = data[3]

pending_users[callback.from_user.id] = {
    "category": category,
    "volume": volume,
    "price": price
}

text = f"""
```

✅ پلن انتخابی:

📦 حجم: <code>{volume}</code>

💰 مبلغ: <code>{price}</code>

━━━━━━━━━━━━━━

💳 شماره کارت:

<code>{CARD_NUMBER}</code>

👤 صاحب کارت:
{CARD_OWNER}

━━━━━━━━━━━━━━

پس از پرداخت،
لطفا عکس رسید را ارسال کن 📸
"""

```
await callback.message.answer(text)
```

@dp.message(F.photo)
async def receive_receipt(message: Message):

```
user_id = message.from_user.id

if user_id not in pending_users:
    return

info = pending_users[user_id]

buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ تایید پرداخت",
                callback_data=f"approve_{user_id}"
            )
        ]
    ]
)

caption = f"""
```

📥 رسید جدید

👤 نام:
{message.from_user.full_name}

🆔 آیدی: <code>{user_id}</code>

📦 پلن:
{info['volume']}

💰 مبلغ:
{info['price']}
"""

```
await bot.send_photo(
    ADMIN_ID,
    photo=message.photo[-1].file_id,
    caption=caption,
    reply_markup=buttons
)

await message.answer(
    "✅ رسیدت ارسال شد.\nبعد از تایید، کانفیگ برات ارسال میشه."
)
```

@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):

```
user_id = int(callback.data.split("_")[1])

await bot.send_message(
    user_id,
    """
```

✅ پرداخت شما تایید شد

🔗 کانفیگ شما:

<code>
vless://example-config
</code>

🙏 ممنون از خریدت ❤️
"""
)

```
await callback.message.answer(
    "✅ کانفیگ برای کاربر ارسال شد."
)
```

async def main():
await dp.start_polling(bot)

if **name** == "**main**":
asyncio.run(main())
