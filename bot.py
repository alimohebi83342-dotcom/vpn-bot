import os
import logging
import urllib.request
import urllib.error
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# 🔒 دریافت اطلاعات حساس از متغیرهای محیطی Railway (امنیت کامل)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

user_states = {}

# 📊 لیست قیمت پلن‌ها بر اساس دلار (مناسب برای درگاه رمز ارز)
PRICES = {
    "pro_1": {"name": "💎 حرفه‌ای | 1 گیگابایت", "usd": 6},
    "pro_5": {"name": "💎 حرفه‌ای | 5 گیگابایت", "usd": 28},
    "pro_10": {"name": "💎 حرفه‌ای | 10 گیگابایت", "usd": 56},
    "pro_20": {"name": "💎 حرفه‌ای | 20 گیگابایت", "usd": 86},
    "pro_50": {"name": "💎 حرفه‌ای | 50 گیگابایت", "usd": 185},
    
    "eco_10": {"name": "🌱 اقتصادی | 10 گیگابایت", "usd": 41},
    "eco_20": {"name": "🌱 اقتصادی | 20 گیگابایت", "usd": 65},
    "eco_40": {"name": "🌱 اقتصادی | 40 گیگابایت", "usd": 116},
}

# 🌐 تابع ساخت لینک پرداخت توکن کریپتو با متد رسمی ناوپیمنتس
def create_crypto_payment(amount_usd, order_id):
    url = "nowpayments.io"
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": float(amount_usd),
        "price_currency": "usd",
        "pay_currency": "usdttrc20",  # پرداخت با تتر شبکه ترون برای کارمزد بسیار کم
        "order_id": str(order_id),
        "order_description": f"Buy VPN Plan Order #{order_id}"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data.get("invoice_url")
            
    except Exception as e:
        logging.error(f"Crypto Gateway Error: {e}")
    return None

# 🚀 منوی استارت شیک و مدرن
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = None
    
    keyboard = [
        [InlineKeyboardButton("💎 سرویس‌های فوق‌حرفه‌ای (VIP)", callback_data="menu_pro")],
        [InlineKeyboardButton("🌱 سرویس‌های اقتصادی (Eco)", callback_data="menu_eco")],
        [InlineKeyboardButton("⚡️ راهنما و قوانین پرداخت", callback_data="crypto_help")]
    ]
    
    await update.message.reply_text(
        f"⚡️ **سلام {update.effective_user.first_name} عزیز، به نسل جدید شبکه امن خوش آمدید!**\n\n"
        "🚀 تمامی سرویس‌ها بر پایه پروتکل‌های نوین ضد فیلتر و با آی‌پی کاملاً ثابت ارائه می‌شوند.\n\n"
        "⚠️ پرداخت در این ربات کاملاً سیستمی و از طریق **ارز دیجیتال (تتر/ترون)** جهت حفظ حریم خصوصی شما انجام می‌شود.\n\n"
        "👇 برای شروع، دسته بندی مورد نظر خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# 🎮 مدیریت دکمه‌های شیشه‌ای منو
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "menu_pro":
        keyboard = [
            [InlineKeyboardButton("🔥 1GB ── 6 USDT", callback_data="buy_pro_1")],
            [InlineKeyboardButton("🔥 5GB ── 28 USDT", callback_data="buy_pro_5")],
            [InlineKeyboardButton("🔥 10GB ── 56 USDT", callback_data="buy_pro_10")],
            [InlineKeyboardButton("🔥 20GB ── 86 USDT", callback_data="buy_pro_20")],
            [InlineKeyboardButton("🔥 50GB ── 185 USDT", callback_data="buy_pro_50")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        await query.edit_message_text("⚡️ **لیست پلن‌های فوق‌حرفه‌ای (سرورهای VIP اختصاصی):**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "menu_eco":
        keyboard = [
            [InlineKeyboardButton("✨ 10GB ── 41 USDT", callback_data="buy_eco_10")],
            [InlineKeyboardButton("✨ 20GB ── 65 USDT", callback_data="buy_eco_20")],
            [InlineKeyboardButton("✨ 40GB ── 116 USDT", callback_data="buy_eco_40")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        await query.edit_message_text("🌱 **لیست پلن‌های اقتصادی (مقرون به صرفه و پایدار):**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "crypto_help":
        keyboard = [[InlineKeyboardButton("🔙 متوجه شدم / بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(
            "🪙 **راهنمای پرداخت با ارز دیجیتال:**\n\n"
            "۱. پس از انتخاب پلن، یک لینک اختصاصی درگاه برای شما ساخته می‌شود.\n"
            "۲. وارد لینک شوید و شبکه انتقال را روی `TRC20` انتخاب کنید.\n"
            "۳. آدرس ولت داده شده را کپی کرده و مبلغ دقیق را از ولت خود (مثل TrustWallet) انتقال دهید.\n"
            "۴. سیستم به طور خودکار تراکنش را تایید می‌کند؛ جهت اطمینان، اسکرین شات نهایی را در ربات بفرستید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "main_menu":
        user_states[user_id] = None
        keyboard = [
            [InlineKeyboardButton("💎 سرویس‌های فوق‌حرفه‌ای (VIP)", callback_data="menu_pro")],
            [InlineKeyboardButton("🌱 سرویس‌های اقتصادی (Eco)", callback_data="menu_eco")],
            [InlineKeyboardButton("⚡️ راهنما و قوانین پرداخت", callback_data="crypto_help")]
        ]
        await query.edit_message_text("👇 لطفاً نوع سرویس مورد نظر خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("buy_"):
        plan_key = query.data.replace("buy_", "")
        plan_info = PRICES.get(plan_key)
        
        if plan_info:
            await query.edit_message_text("⏳ **در حال ایجاد فاکتور ایمن و درگاه آنلاین کریپتو...**")
            
            # ساخت لینک درگاه
            invoice_url = create_crypto_payment(plan_info["usd"], f"{user_id}_{plan_key}")
            
            if invoice_url:
                user_states[user_id] = {"status": "waiting_receipt", "plan": plan_info}
                keyboard = [
                    [InlineKeyboardButton("💳 ورود به درگاه پرداخت آنلاین تتر", url=invoice_url)],
                    [InlineKeyboardButton("🔙 انصراف و بازگشت", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(
                    f"🛒 **فاکتور خرید شما صادر شد**\n\n"
                    f"📦 سرویس: *{plan_info['name']}*\n"
                    f"💵 مبلغ فاکتور: `{plan_info['usd']}` **USDT (تتر شبکه TRC20)**\n\n"
                    f"📣 **اقدام بعدی:** روی دکمه زیر کلیک کنید، تراکنش را انجام دهید و پس از اتمام، **تصویر رسید موفقیت‌آمیز** یا کد هش تراکنش را در همینجا ارسال کنید تا سفارش تحویل داده شود.",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    "❌ **خطا در اتصال به درگاه پرداخت دیجیتال.**\n"
                    "مشکلی در ارتباط با صرافی مرکزی رخ داده است. لطفاً چند لحظه دیگر دوباره تلاش کنید یا به پشتیبانی پیام دهید.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]])
                )

# 📩 دریافت فیش یا هش رمزارز و ارسال به ادمین برای ارسال کانفیگ
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = user_states.get(user_id)
    
    if not user_data or user_data.get("status") != "waiting_receipt":
        await update.message.reply_text("❌ لطفاً ابتدا از منوی خرید، یک پلن انتخاب کنید.")
        return

    plan_info = user_data["plan"]
    username = f"@{update.effective_user.username}" if update.effective_user.username else "بدون یوزرنیم"

    admin_text = (
        f"💰 **اعلام واریز کریپتو (نیاز به تحویل کانفیگ)**\n\n"
        f"👤 کاربر: {update.effective_user.full_name} ({username})\n"
        f"🆔 آیدی عددی: `{user_id}`\n"
        f"🛍 سرویس خریده شده: *{plan_info['name']}*\n"
        f"💵 مبلغ درگاه: `{plan_info['usd']}` USDT\n"
    )

    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=admin_text, parse_mode="Markdown")
    elif update.message.text:
        admin_text += f"💬 متن ارسالی کاربر (احتمالاً کد تراکنش):\n`{update.message.text}`"
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لطفا رسید پرداخت را به صورت عکس یا کد تراکنش متنی ارسال کنید.")
        return

    await update.message.reply_text(
        "✅ **تراکنش شما ثبت و برای ادمین ارسال شد.**\n\n"
        "تاییدیه پرداخت‌های کریپتو معمولاً بین ۵ الی ۱۵ دقیقه زمان می‌برد. به محض تایید، کانفیگ اختصاصی شما در همین چت ارسال خواهد شد. از اعتماد شما سپاسگزاریم! ✨"
    )
    user_states[user_id] = None

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN variable is not set!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_receipt))

    print("🤖 ربات مدرن کریپتویی فروش کانفیگ با موفقیت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
