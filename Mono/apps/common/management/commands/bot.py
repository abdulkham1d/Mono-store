import logging

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
# Telegram bot kutubxonalari
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Django modellarni import qilish
from apps.common.models import User_tg  # O'zingizning app nomingizga o'zgartiring

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokenini settings.py ga qo'shing yoki bu yerga yozing
BOT_TOKEN = "Your bot token"  # O'zingizning tokeningizni qo'ying


class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Handlerlarni sozlash"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(MessageHandler(filters.CONTACT, self.handle_contact))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandasi handler"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        try:
            logger.info(f"Start command received from user: {user.id}")

            # Foydalanuvchini bazadan qidirish (async)
            db_user = await sync_to_async(User_tg.objects.filter(id=user.id).first)()
            logger.info(f"Database query result: {db_user}")

            if db_user:
                # Agar foydalanuvchi mavjud bo'lsa, welcome back ko'rsatish
                logger.info(f"Existing user found: {db_user.first_name}")
                await self.send_welcome_back(update, db_user)
            else:
                # Yangi foydalanuvchi bo'lsa, telefon raqam so'rash
                logger.info("New user, requesting phone number")
                await self.request_phone_number(update, user)

        except Exception as e:
            import traceback
            logger.error(f"Start command error: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

    async def request_phone_number(self, update: Update, user):
        """Telefon raqam so'rash"""
        # Telefon raqam so'rash tugmasi
        contact_button = KeyboardButton(
            text="📱 Telefon raqamni yuborish",
            request_contact=True
        )
        reply_markup = ReplyKeyboardMarkup(
            [[contact_button]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        welcome_text = (
            f"Assalomu alaykum {user.first_name}! 👋\n\n"
            "Botdan foydalanish uchun telefon raqamingizni yuboring.\n"
            "Pastdagi tugmani bosing:"
        )

        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telefon raqam yuborilganda ishlaydigan handler"""
        contact = update.message.contact
        user = update.effective_user

        try:
            # Foydalanuvchi ma'lumotlarini bazaga saqlash (async)
            db_user, created = await sync_to_async(User_tg.objects.get_or_create)(
                id=user.id,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'phone': contact.phone_number,
                    'bio': user.language_code if hasattr(user, 'language_code') else None,
                    'last_login': True
                }
            )

            if not created:
                # Agar foydalanuvchi mavjud bo'lsa, ma'lumotlarni yangilash
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
                db_user.username = user.username
                db_user.phone = contact.phone_number
                db_user.last_login = True
                await sync_to_async(db_user.save)()

            # Muvaffaqiyatli ro'yxatdan o'tgach welcome back ko'rsatish
            await self.send_welcome_back(update, db_user)

        except Exception as e:
            import traceback
            logger.error(f"Contact handling error: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            await update.message.reply_text(
                "Telefon raqamni saqlashda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring."
            )

    async def send_welcome_back(self, update: Update, db_user: User_tg):
        """Welcome back xabari yuborish"""
        # Klaviaturani olib tashlash
        from telegram import ReplyKeyboardRemove

        # Last name bo'lsa ko'rsatish, aks holda first name
        display_name = db_user.last_name if db_user.last_name else db_user.first_name

        welcome_text = f"Welcome back, {display_name}! 🎉"

        # Website ga o'tish tugmasi
        inline_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Visit website", url="https://t.me/Mono_store_bot/App")]
        ])

        await update.message.reply_text(
            welcome_text,
            reply_markup=ReplyKeyboardRemove()
        )

        await update.message.reply_text(
            "Quyidagi tugma orqali websitega o'ting:",
            reply_markup=inline_keyboard
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline keyboard tugmalari uchun handler"""
        query = update.callback_query
        await query.answer()

        # Bu yerda qo'shimcha callback handlerlar qo'shishingiz mumkin

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Boshqa xabarlar uchun handler"""
        user = update.effective_user

        try:
            # Foydalanuvchi ro'yxatdan o'tganmi tekshirish (async)
            db_user = await sync_to_async(User_tg.objects.filter(id=user.id).first)()

            if not db_user:
                await self.request_phone_number(update, user)
            else:
                # Foydalanuvchi ro'yxatdan o'tgan bo'lsa
                await update.message.reply_text(
                    "Sizning xabaringiz qabul qilindi. /start tugmasini bosing."
                )

        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text("Xatolik yuz berdi.")

    def run(self):
        """Botni ishga tushirish"""
        logger.info("Bot ishga tushmoqda...")
        self.application.run_polling(drop_pending_updates=True)


class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Bot token (ixtiyoriy)',
        )

    def handle(self, *args, **options):
        """Django management command handler"""

        # Agar token argument sifatida berilgan bo'lsa
        if options['token']:
            global BOT_TOKEN
            BOT_TOKEN = options['token']

        self.stdout.write(
            self.style.SUCCESS('Telegram bot ishga tushmoqda...')
        )

        try:
            # Bot instance yaratish va ishga tushirish
            bot = TelegramBot()
            bot.run()

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Bot to\'xtatildi.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Xatolik: {e}')
            )
