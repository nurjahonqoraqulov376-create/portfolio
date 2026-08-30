"""
Telegram chat ID'ni topish uchun yordamchi buyruq.

Ishlatish:
  1. `.env` ga TELEGRAM_BOT_TOKEN=... yozing (@BotFather bergan token).
  2. Telegram'da o'z botingizni toping va `/start` bosing.
  3. `python manage.py telegram_chat_id`
  4. Chiqqan raqamni `.env` ga TELEGRAM_CHAT_ID=... deb qo'ying.

Nega kerak: Bot API `@username` bilan emas, faqat raqamli chat ID bilan
ishlaydi va bot birinchi bo'lib yoza olmaydi — siz `/start` bosishingiz shart.
"""

from django.core.management.base import BaseCommand, CommandError

from core.telegram import call_api


class Command(BaseCommand):
    help = "Botga yozgan chatlarning ID'sini ko'rsatadi (TELEGRAM_CHAT_ID uchun)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--send-test",
            metavar="CHAT_ID",
            help="Shu chat ID'ga sinov xabari yuboradi.",
        )

    def handle(self, *args, **options):
        chat_id = options.get("send_test")
        if chat_id:
            return self._send_test(chat_id)

        try:
            response = call_api("getUpdates", {})
        except RuntimeError as error:
            raise CommandError(str(error))
        except Exception as error:
            raise CommandError(f"Telegram'ga ulanib bo'lmadi: {error}")

        if not response.get("ok"):
            raise CommandError(f"Telegram javobi: {response}")

        # Bir chat bir necha marta yozgan bo'lishi mumkin — takrorlanmasin
        chats = {}
        for update in response.get("result", []):
            payload = update.get("message") or update.get("channel_post") or {}
            chat = payload.get("chat")
            if chat:
                chats[chat["id"]] = chat

        if not chats:
            self.stdout.write(
                self.style.WARNING(
                    "Hech qanday chat topilmadi.\n"
                    "Telegram'da botingizga kirib `/start` bosing, so'ng "
                    "shu buyruqni qayta ishga tushiring.\n"
                    "(Eslatma: agar botga webhook o'rnatilgan bo'lsa, "
                    "getUpdates bo'sh qaytadi.)"
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("Topilgan chatlar:"))
        for identifier, chat in chats.items():
            name = chat.get("username") or chat.get("title") or chat.get("first_name", "")
            self.stdout.write(f"  TELEGRAM_CHAT_ID={identifier}   ({chat.get('type')}: {name})")

    def _send_test(self, chat_id):
        try:
            response = call_api(
                "sendMessage",
                {
                    "chat_id": chat_id,
                    "text": "✅ Portfolio saytidan sinov xabari — sozlash ishladi.",
                },
            )
        except Exception as error:
            raise CommandError(f"Yuborib bo'lmadi: {error}")

        if not response.get("ok"):
            raise CommandError(f"Telegram javobi: {response}")
        self.stdout.write(self.style.SUCCESS("Sinov xabari yuborildi."))
