# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.dbusers import db
from config import ADMINS

FWD_SETTINGS = {}

async def load_fwd_settings():
    global FWD_SETTINGS
    FWD_SETTINGS = await db.get_forward_settings()

# Load settings at startup
asyncio.create_task(load_fwd_settings())

@Client.on_message((filters.channel | filters.private) & filters.incoming)
async def forward_message_handler(client: Client, message: Message):
    if not FWD_SETTINGS.get("enabled"):
        return

    source_channels = FWD_SETTINGS.get("source_channels", [])
    if message.chat.id not in source_channels:
        return

    # Keyword filtering
    if FWD_SETTINGS.get("filter_keywords"):
        content = message.text or message.caption
        if not content or not any(keyword.lower() in content.lower() for keyword in FWD_SETTINGS["filter_keywords"]):
            return

    use_copy = FWD_SETTINGS.get("as_copy") or FWD_SETTINGS.get("header") or FWD_SETTINGS.get("footer")
    destination_channels = FWD_SETTINGS.get("destination_channels", [])

    for dest_channel in destination_channels:
        try:
            if use_copy:
                new_caption = ""
                original_text = message.text or message.caption or ""
                header = FWD_SETTINGS.get("header", "")
                footer = FWD_SETTINGS.get("footer", "")

                if header:
                    new_caption += header + "\n"

                new_caption += original_text

                if footer:
                    new_caption += "\n" + footer

                if message.media:
                    await message.copy(dest_channel, caption=new_caption.strip())
                else:
                    await client.send_message(dest_channel, new_caption.strip())
            else:
                await message.forward(dest_channel)
        except Exception as e:
            print(f"Error forwarding message to {dest_channel}: {e}")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_status"))
async def fwd_status_cmd(client, message):
    status = f"""**Forwarding Status**

**Enabled:** `{FWD_SETTINGS.get('enabled')}`
**Forward as Copy:** `{FWD_SETTINGS.get('as_copy')}`

**Source Channels:** `{FWD_SETTINGS.get('source_channels')}`
**Destination Channels:** `{FWD_SETTINGS.get('destination_channels')}`

**Filter Keywords:** `{FWD_SETTINGS.get('filter_keywords')}`
**Header:** `{FWD_SETTINGS.get('header')}`
**Footer:** `{FWD_SETTINGS.get('footer')}`
    """
    await message.reply_text(status)

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_toggle"))
async def fwd_toggle_cmd(client, message):
    FWD_SETTINGS["enabled"] = not FWD_SETTINGS.get("enabled", False)
    await db.update_forward_settings(FWD_SETTINGS)
    await message.reply_text(f"Forwarding enabled: `{FWD_SETTINGS['enabled']}`")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_toggle_copy"))
async def fwd_toggle_copy_cmd(client, message):
    FWD_SETTINGS["as_copy"] = not FWD_SETTINGS.get("as_copy", False)
    await db.update_forward_settings(FWD_SETTINGS)
    await message.reply_text(f"Forward as copy: `{FWD_SETTINGS['as_copy']}`")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_add_source"))
async def fwd_add_source_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/fwd_add_source <chat_id>`")
    try:
        chat_id = int(message.command[1])
        if chat_id not in FWD_SETTINGS["source_channels"]:
            FWD_SETTINGS["source_channels"].append(chat_id)
            await db.update_forward_settings(FWD_SETTINGS)
        await message.reply_text(f"Source channels: `{FWD_SETTINGS['source_channels']}`")
    except ValueError:
        await message.reply_text("Invalid chat_id.")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_rem_source"))
async def fwd_rem_source_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/fwd_rem_source <chat_id>`")
    try:
        chat_id = int(message.command[1])
        if chat_id in FWD_SETTINGS["source_channels"]:
            FWD_SETTINGS["source_channels"].remove(chat_id)
            await db.update_forward_settings(FWD_SETTINGS)
        await message.reply_text(f"Source channels: `{FWD_SETTINGS['source_channels']}`")
    except ValueError:
        await message.reply_text("Invalid chat_id.")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_add_dest"))
async def fwd_add_dest_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/fwd_add_dest <chat_id>`")
    try:
        chat_id = int(message.command[1])
        if chat_id not in FWD_SETTINGS["destination_channels"]:
            FWD_SETTINGS["destination_channels"].append(chat_id)
            await db.update_forward_settings(FWD_SETTINGS)
        await message.reply_text(f"Destination channels: `{FWD_SETTINGS['destination_channels']}`")
    except ValueError:
        await message.reply_text("Invalid chat_id.")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_rem_dest"))
async def fwd_rem_dest_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/fwd_rem_dest <chat_id>`")
    try:
        chat_id = int(message.command[1])
        if chat_id in FWD_SETTINGS["destination_channels"]:
            FWD_SETTINGS["destination_channels"].remove(chat_id)
            await db.update_forward_settings(FWD_SETTINGS)
        await message.reply_text(f"Destination channels: `{FWD_SETTINGS['destination_channels']}`")
    except ValueError:
        await message.reply_text("Invalid chat_id.")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_add_keyword"))
async def fwd_add_keyword_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/fwd_add_keyword <keyword>`")
    keyword = " ".join(message.command[1:])
    if keyword not in FWD_SETTINGS["filter_keywords"]:
        FWD_SETTINGS["filter_keywords"].append(keyword)
        await db.update_forward_settings(FWD_SETTINGS)
    await message.reply_text(f"Filter keywords: `{FWD_SETTINGS['filter_keywords']}`")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_rem_keyword"))
async def fwd_rem_keyword_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/fwd_rem_keyword <keyword>`")
    keyword = " ".join(message.command[1:])
    if keyword in FWD_SETTINGS["filter_keywords"]:
        FWD_SETTINGS["filter_keywords"].remove(keyword)
        await db.update_forward_settings(FWD_SETTINGS)
    await message.reply_text(f"Filter keywords: `{FWD_SETTINGS['filter_keywords']}`")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_set_header"))
async def fwd_set_header_cmd(client, message):
    if len(message.command) < 2:
        FWD_SETTINGS["header"] = ""
    else:
        FWD_SETTINGS["header"] = " ".join(message.command[1:])
    await db.update_forward_settings(FWD_SETTINGS)
    await message.reply_text(f"Header set to: `{FWD_SETTINGS['header']}`")

@Client.on_message(filters.user(ADMINS) & filters.command("fwd_set_footer"))
async def fwd_set_footer_cmd(client, message):
    if len(message.command) < 2:
        FWD_SETTINGS["footer"] = ""
    else:
        FWD_SETTINGS["footer"] = " ".join(message.command[1:])
    await db.update_forward_settings(FWD_SETTINGS)
    await message.reply_text(f"Footer set to: `{FWD_SETTINGS['footer']}`")
