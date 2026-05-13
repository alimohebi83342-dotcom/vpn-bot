import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# 🛑 تنظیمات اصلی ربات (اطلاعات خود را جایگزین کنید)
BOT_TOKEN = "توکن_ربات_شما"
ADMIN_ID = 123456789  # آیدی عددی تلگرام شما برای دریافت فیش‌ها
CARD_NUMBER = "6037991122334455"  # شماره کارت بانکی شما
CARD_HOLDER = "نام صاحب کارت"
NOWPAYMENTS_API_KEY = "کلید_ای_پی_ای_ناو_پیمنت" # اگر ندارید خالی بگذارید

# تنظیمات لاگر برای عیب‌یابی
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# دیتاپیس موقت در حافظه برای پیگیری وضعیت کاربران
user_states = {}

# 📊 لیست قیمت پلن‌ها
PRICES = {
    "pro_1": {"name": "حرفه‌ای 1GB", "price": 360000, "usd": 6},
    "pro_5": {"name": "حرفه‌ای 5GB", "price": 1690000, "usd": 28},
    "pro_10": {"name": "حرفه‌ای 10GB", "price": 3400000, "usd": 56},
    "pro_20": {"name": "حرفه‌ای 20GB", "price": 5200000, "usd": 86},
    "pro_50": {"name": "حرفه‌ای 50GB", "price": 11200000, "usd": 185},
    
    "eco_10": {"name": "اقتصادی 10GB", "price": 2500000, "usd": 41},
    "eco_20": {"name": "اقتصادی 20GB", "price": 3900000, "usd": 65},
    "eco_40": {"name": "اقتصادی 40GB", "price": 7000000, "usd": 116},
}

# 🌐 اتصال به درگاه ارز دیجیتال (NowPayments)
def create_crypto_payment(amount_usd, order_id):
    url = "nowpayments.io"
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": amount_usd,
        "price_currency": "usd",
        "pay_currency": "usdttrc20", # دریافت به صورت تتر شبکه ترون
        "order_id": str(order_id),
        "ipn_callback_url": "https://example.com"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            return response.json().get("invoice_url")
    except Exception as e:
        logging.error(f"Crypto payment error: {e}")
    return None

# 🚀 دستور استارت و خوش‌آمدگویی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = None # ریست کردن وضعیت کاربر
    
    keyboard = [
        [InlineKeyboardButton("💎 خرید سرویس حرفه‌ای", callback_data="menu_pro")],
        [InlineKeyboardButton("🌱 خرید سرویس اقتصادی", callback_data="menu_eco")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"سلام {update.effective_user.first_name} عزیز! ☀️\n"
        "به فروشگاه کانفیگ خوش آمدید.\n"
        "لطفاً نوع سرویس مورد نظر خود را انتخاب کنید:",
        reply_markup=reply_markup
    )

# 🎮 مدیریت دکمه‌های شیشه‌ای
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "menu_pro":
        keyboard = [
            [InlineKeyboardButton("1GB (360,000 تومان)", callback_data="buy_pro_1")],
            [InlineKeyboardButton("5GB (1,690,000 تومان)", callback_data="buy_pro_5")],
            [InlineKeyboardButton("10GB (3,400,000 تومان)", callback_data="buy_pro_10")],
            [InlineKeyboardButton("20GB (5,200,000 تومان)", callback_data="buy_pro_20")],
            [InlineKeyboardButton("50GB (11,200,000 تومان)", callback_data="buy_pro_50")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        await query.edit_message_text("⚡️ لیست سرویس‌های **حرفه‌ای**:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "menu_eco":
        keyboard = [
            [InlineKeyboardButton("10GB (2,500,000 تومان)", callback_data="buy_eco_10")],
            [InlineKeyboardButton("20GB (3,900,000 تومان)", callback_data="buy_eco_20")],
            [InlineKeyboardButton("40GB (7,000,000 تومان)", callback_data="buy_eco_40")],
            [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
        ]
        await query.edit_message_text("🌱 لیست سرویس‌های **اقتصادی**:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "main_menu":
        user_states[user_id] = None
        keyboard = [
            [InlineKeyboardButton("💎 خرید سرویس حرفه‌ای", callback_data="menu_pro")],
            [InlineKeyboardButton("🌱 خرید سرویس اقتصادی", callback_data="menu_eco")]
        ]
        await query.edit_message_text("لطفاً نوع سرویس مورد نظر خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("buy_"):
        plan_key = query.data.replace("buy_", "")
        plan_info = PRICES.get(plan_key)
        
        if plan_info:
            # ذخیره سفارش کاربر در دیتابیس حافظه
            user_states[user_id] = {"status": "waiting_method", "plan": plan_info}
            
            keyboard = [
                [InlineKeyboardButton("💳 کارت به کارت (ایران)", callback_data=f"pay_card_{plan_key}")],
                [InlineKeyboardButton("🪙 ارز دیجیتال (تتر/ترون)", callback_data=f"pay_crypto_{plan_key}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
            ]
            await query.edit_message_text(
                f"🛍 سفارش شما: *{plan_info['name']}*\n"
                f"💰 مبلغ قابل پرداخت: *{plan_info['price']:,} تومان*\n\n"
                "👇 لطفاً روش پرداخت خود را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

    elif query.data.startswith("pay_card_"):
        plan_key = query.data.replace("pay_card_", "")
        plan_info = PRICES.get(plan_key)
        user_states[user_id] = {"status": "waiting_receipt", "plan": plan_info, "method": "Card"}
        
        message_text = (
            f"📥 **روش کارت به کارت انتخاب شد**\n\n"
            f"📌 سرویس: {plan_info['name']}\n"
            f"💵 مبلغ دقیق برای واریز:\n`{plan_info['price']}` تومان\n\n"
            f"💳 شماره کارت جهت واریز:\n`{CARD_NUMBER}`\n"
            f"👤 به نام: {CARD_HOLDER}\n\n"
            f"⚠️ **مهم:** پس از واریز، روی مبالغ یا شماره کارت بالا ضربه بزنید تا کپی شوند. "
            f"سپس **عکس رسید واریزی خود را همین‌جا در ربات بفرستید** تا سفارش شما بررسی و تأیید شود."
        )
        await query.edit_message_text(message_text, parse_mode="Markdown")

    elif query.data.startswith("pay_crypto_"):
        plan_key = query.data.replace("pay_crypto_", "")
        plan_info = PRICES.get(plan_key)
        
        await query.edit_message_text("⏳ در حال ساخت لینک پرداخت رمز ارز...")
        
        invoice_url = create_crypto_payment(plan_info["usd"], f"{user_id}_{plan_key}")
        
        if invoice_url:
            user_states[user_id] = {"status": "waiting_receipt", "plan": plan_info, "method": "Crypto"}
            keyboard = [[InlineKeyboardButton("🔗 ورود به درگاه پرداخت دیجیتال", url=invoice_url)]]
            
            await query.edit_message_text(
                f"🪙 **پرداخت دیجیتال با تتر (USDT-TRC20)**\n\n"
                f"📌 سرویس: {plan_info['name']}\n"
                f"💵 مبلغ ارزی: `{plan_info['usd']}` دلار\n\n"
                f"👇 روی دکمه زیر کلیک کنید و پرداخت را انجام دهید. "
                f"پس از اتمام یا اسکرین‌شات موفقی، فیش یا شناسه را ارسال کنید:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "❌ خطا در اتصال به درگاه رمز ارز. لطفاً از روش کارت به کارت استفاده کنید یا به پشتیبانی پیام دهید.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]])
            )

# 📩 دریافت فیش و ارسال به ادمین برای تایید
async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = user_states.get(user_id)
    
    # بررسی اینکه آیا کاربر در مرحله ارسال فیش هست یا خیر
    if not user_data or user_data.get("status") != "waiting_receipt":
        await update.message.reply_text("❌ لطفاً ابتدا از منو خرید، یک پلن انتخاب کنید.")
        return

    plan_info = user_data["plan"]
    method = user_data["method"]
    username = f"@{update.effective_user.username}" if update.effective_user.username else "بدون یوزرنیم"

    # ارسال اطلاعات به ادمین برای تایید دستی (چون مشتری زیاد نیست از تایید دستی استفاده میکنیم)
    admin_text = (
        f"🚨 **رسید پرداخت جدید دریافت شد!**\n\n"
        f"👤 کاربر: {update.effective_user.full_name} ({username})\n"
        f"🆔 آیدی عددی: `{user_id}`\n"
        f"🛍 سرویس درخواستی: *{plan_info['name']}*\n"
        f"💵 مبلغ: {plan_info['price']:,} تومان ({plan_info['usd']}$)\n"
        f"⚙️ روش پرداخت: {method}\n"
    )

    if update.message.photo:
        # اگر کاربر عکس فرستاد
        photo_file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=admin_text, parse_mode="Markdown")
    elif update.message.document:
        # اگر کاربر به صورت فایل فرستاد
        doc_file_id = update.message.document.file_id
        await context.bot.send_document(chat_id=ADMIN_ID, document=doc_file_id, caption=admin_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لطفا رسید خود را به صورت عکس یا فایل ارسال کنید.")
        return

    # پیام نهایی به مشتری
    await update.message.reply_text(
        "✅ **رسید شما با موفقیت برای مدیریت ارسال شد.**\n\n"
        "پس از بررسی و تایید واریزی توسط تیم پشتیبانی، کانفیگ اختصاصی شما از طریق همین ربات برایتان ارسال خواهد شد. از شکیبایی شما سپاسگزاریم. 🙏"
    )
    
    # پاک کردن وضعیت کاربر بعد از ارسال موفقیت‌آمیز فیش
    user_states[user_id] = None

# 🏗 متد اصلی راه‌اندازی ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    # هندلر برای عکس، فایل یا متن ارسالی به عنوان فیش
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, handle_receipt))

    print("🤖 ربات فروش با موفقیت روشن شد و در حال کار است...")
    app.run_polling()

if __name__ == "__main__":
    main()
