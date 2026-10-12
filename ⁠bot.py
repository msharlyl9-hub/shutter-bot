import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import exifread
import io

# إعداد التسجيل للمساعدة في تتبع الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# وضع توكن البوت الخاص بك هنا
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! أرسل لي صورة من كاميرا Nikon (كـ ملف Document للحفاظ على البيانات) لأقوم بقراءة عدد الشتر لك."
    )

async def process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # جلب الملف
    document = update.message.document or update.message.photo[-1]
    file = await context.bot.get_file(document.file_id)
    
    # تنزيل الصورة في الذاكرة
    image_bytes = await file.download_as_bytearray()
    image_file = io.BytesIO(image_bytes)
    
    # قراءة بيانات EXIF
    tags = exifread.process_file(image_file)
    
    # البحث عن تاغ الشتر الخاص بكاميرات نيكون
    shutter_count = None
    for tag in tags.keys():
        if "TotalNumberOfISOSpeedRatings" in tag or "Image Tag 0xA432" in tag or "MakerNote TotalIndex" in tag:
            shutter_count = tags[tag]
            break
        elif "ShutterCount" in tag or "Image Tag 0x0093" in tag:
            shutter_count = tags[tag]
            break

    if shutter_count:
        await update.message.reply_text(f"📸 عدد شتر الكاميرا: {shutter_count}")
    else:
        await update.message.reply_text(
            "لم أتمكن من قراءة عدد الشتر. يرجى التأكد من إرسال الصورة الأصلية كـ (File/Document) وليس كـ صورة عادية."
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, process_photo))
    
    print("Bot is running...")
    app.run_polling()
