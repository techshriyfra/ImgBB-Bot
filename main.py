import asyncio
import os
import shutil
import traceback
from flask import Flask
import imgbbpy
import pyromod.listen  # Ensure pyromod is installed
from pyrogram import Client, filters
from pyromod.helpers import ikb

from utils.configs import Tr, Var

# Initialize Flask app for Koyeb
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Imgbb Bot is running!"

# Initialize Telegram Client
Img = Client(
    "ImgBB Bot",
    bot_token=Var.BOT_TOKEN,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
)

Imgclient = imgbbpy.SyncClient(Var.API)

@app.route('/health')
def health():
    return "OK", 200

START_BTN = ikb([
    [("👾 About", "about"), ("📚 Help", "help")],
    [("👨‍💻 Developer", "https://bio.link/aminesoukara", "url"), ("❌ Close", "close")],
])

HOME_BTN = ikb([[("🏠 Home", "home"), ("❌ Close", "close")]])
CLOSE_BTN = [("❌ Close", "close")]

@Img.on_callback_query()
async def cdata(c, q):
    chat_id = q.from_user.id
    data = q.data
    wait = Tr.WAIT

    if data == "home":
        await q.answer(wait)
        await q.message.edit_text(
            text=Tr.START_TEXT.format(q.from_user.mention),
            reply_markup=START_BTN,
            disable_web_page_preview=True,
        )
    elif data == "help":
        await q.answer(wait)
        await q.message.edit_text(
            text=Tr.HELP_TEXT, reply_markup=HOME_BTN, disable_web_page_preview=True
        )
    elif data == "about":
        await q.answer(wait)
        await q.message.edit_text(
            text=Tr.ABOUT_TEXT,
            reply_markup=HOME_BTN,
            disable_web_page_preview=True,
        )
    elif data == "close":
        await q.message.delete(True)
        try:
            await q.message.reply_to_message.delete(True)
        except:
            pass
    elif data.startswith("del_"):
        exp = int(data.split("_")[1]) if data.split("_")[1] != "0" else None
        await q.answer(wait)
        r = q.message.reply_to_message
        filename = f"Uploaded-{chat_id}"
        tmp = os.path.join("downloads", str(chat_id))
        os.makedirs(tmp, exist_ok=True)
        dwn = await q.message.reply_text("✅ Downloading ...", True)
        img_path = await r.download()
        await dwn.edit_text("⭕ Uploading ...")
        await dwn.delete()
        try:
            image = Imgclient.upload(file=img_path, expiration=exp, name=filename)
        except Exception as error:
            traceback.print_exc()
            await q.message.reply(f"⚠️ Ops, Something Went Wrong!\n\n**•Log: ** {error}")
            return
        done = f"""
🔗 **Link:** `{image.url}`
📝 **Filename:** `{image.filename}`
💾 **Size:** {image.size}B
⚠️ **Delete URL:** `{image.delete_url}`
⏳ **Expiration:** {exp if exp else 'No Expiry'}
        """
        imgkb = ikb([
            [("🔗 Open", image.url, "url"), ("⚠️ Delete", image.delete_url, "url")],
            [("❌ Close", "close")]
        ])
        await q.message.reply(done, disable_web_page_preview=True, reply_markup=imgkb)
        shutil.rmtree(tmp, ignore_errors=True)

@Img.on_message(filters.private & filters.command(["start"]))
async def start(c, m):
    await m.reply_photo(
        photo=Var.START_PIC,
        caption=Tr.START_TEXT.format(m.from_user.mention),
        reply_markup=START_BTN,
        quote=True,
    )

@Img.on_message(
    filters.private & (filters.photo | filters.sticker | filters.document | filters.animation)
)
async def getimglink(c, m):
    if not Var.API:
        return await m.reply_text(Tr.ERR_TEXT, quote=True)
    BTN = ikb([
        [("▫️ 5 Min", "del_300"), ("▫️ 15 Min", "del_900"), ("▫️ 30 Min", "del_1800")],
        [("▪️ 1 Hour", "del_3600"), ("▪️ 2 Hours", "del_7200"), ("▪️ 6 Hours", "del_21600"), ("▪️ 12 Hours", "del_43200")],
        [("◽ 1 Day", "del_86400"), ("◽ 2 Days", "del_172800"), ("◽ 3 Days", "del_259200")],
        [("◾ 1 Week", "del_604800"), ("◾ 2 Weeks", "del_1209600"), ("◾ 1 Month", "del_2629800"), ("◾ 2 Months", "del_5259600")],
        [("◻ Don't AutoDelete ◼", "del_0")],
        [("❌ Close", "close")],
    ])
    await m.reply_text("🗑 Select AutoDelete Time:", reply_markup=BTN, quote=True)

async def run():
    await Img.start()
    print("Bot is running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    import threading
    loop = asyncio.get_event_loop()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080, debug=False)).start()
    loop.create_task(run())
    loop.run_forever()
