from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, RPCError
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, ChatIdInvalid, MessageEmpty, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup   
from pyromod import listen
import os
import datetime as dt
from time import sleep
from pyromod import listen
import asyncio
from config import api_id, api_hash, bot_token, ADMINS, timeout
from helpers.database import *
from helpers.helpers import get_readable_time
import logging
import sys
import pytz


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
					level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logger = logging.getLogger()
start_time = dt.datetime.now()




try: 
	app = Client(name="pyro",api_id=api_id, api_hash=api_hash, bot_token=bot_token)
	logger.info("Bot started")
except Exception as e:
	logger.error(e)
	sys.exit()

# Some Markups

start_markup = InlineKeyboardMarkup([[
	InlineKeyboardButton("Ask any query", url="https://t.me/TheQuantum_Bot")
],
[
	InlineKeyboardButton("Getting Channel Id", callback_data = "help")
]])

back_markup = InlineKeyboardMarkup([[
	InlineKeyboardButton("Back", callback_data="back")
]])

error_markup = InlineKeyboardMarkup([[
	InlineKeyboardButton("Report the Error", url="https://t.me/TheQuantum_Bot")
]])


async def edit_message(msg, id , i, sf):
	try:
		if msg.document or msg.video or msg.audio:
			await app.edit_message_caption(chat_id = id, message_id = i, caption = sf)
		else:
			await app.edit_message_text(chat_id = id, message_id = i, text = sf)
	except FloodWait as e:
		await asyncio.sleep(e.value)
		await edit_message(msg, id , i , sf)
	except Exception as e:
		logger.error(e)


async def send_message(chat_id, text, reply_markup = None):
	try:
		await app.send_message(chat_id = chat_id, text = text, reply_markup = reply_markup)
	except FloodWait as e:
		await asyncio.sleep(e.value)
		await send_message(chat_id, text, reply_markup)
	except Exception as e:
		logger.error(e)


@app.on_message(filters.command('custom_caption') & filters.user(ADMINS))
async def suffix(client, message):
	user_id = message.from_user.id


	ask_mode = await client.ask(user_id, "Send me which mode you want to run\nCustom_Caption or Replace or Remove")
	try:
		mode = ask_mode.text
		if mode not in ["Custom_Caption", "Replace", "Remove"]:
			await message.reply("Mode not found")
			return
	except:
		await message.reply("Mode not found")
		return


	id = await client.ask(user_id, "Send me the id of the channel where you want to add custom caption\n( do not add -100 to id")
	try:
		id = int("-100"+ id.text)
	except Exception:
		await message.reply("Wrong Channel id")
		return

	start_id = await client.ask(user_id, "Send me the id of the message from where you want to add custom caption")
	try:
		start_id = int(start_id.text)
	except Exception:
		await message.reply("Must be integer")
		return


	end_id = await client.ask(user_id, "Send me the id of the message from where you want to end adding custom caption")
	try:
		end_id = int(end_id.text)
	except Exception:
		await message.reply("Must be Integer")
		return


	suffix = await client.ask(user_id, "Now send the custom caption or thing to be replaced or removed\n\n{caption} - old caption")
	try:
		suffix = suffix.text
		if suffix:
			pass
		else:
			raise ValueError("Send a valid value")

	except Exception:
		await message.reply("Wrong Value")
		return

	if mode == "Replace":
		replace = await client.ask(user_id, "Send the new string")
		try:
			replace = replace.text
			if replace:
				pass
			else:
				raise ValueError("Send a valid value")

		except Exception:
			await message.reply("Wrong Value")
			return

	i = start_id
	temp = await message.reply_text("Started adding your custom caption....")
	while i<end_id + 1:
		msg = await app.get_messages(id, i)
		try:
			
			if msg.document or msg.video or msg.audio or msg.media:
				cap1 = msg.caption
			else: 
				cap1 = msg.text

			if mode == "Custom_Caption":
				if cap1:
					if msg.media:
						caption = f"{msg.caption}"
					else:
						caption = cap1
				else:
					media = msg.document or msg.video or msg.audio or msg.media
					fname = media.file_name
					caption = fname.replace("_", ".")
				sf = suffix.format(caption=caption)
			elif mode == "Replace":
				if cap1:
					sf = cap1.replace(suffix, replace)
				else:
					i+=1
					continue

			elif mode == "Remove":
				if cap1:
					sf = cap1.replace(suffix, "")
				else:
					i+=1
					continue


			if cap1 == sf:
				i+=1
				continue
				
			await edit_message(msg, id , i , sf)
			
		except Exception as e:
			logger.error(e)

		i+=1
		
	await temp.delete()
	await message.reply_text("Done")


@app.on_message(filters.command('forward') & filters.private)
async def forward(client, message):

	if await is_banned_user(message.from_user.id):
		return None
	await add_user(message.from_user.id, message.from_user.first_name)
	
	user_id = message.from_user.id


	target_id = await client.ask(user_id, "Send me the id of the target channel\n( do not add -100 to id")

	try:
		target_id = int("-100"+ target_id.text)
	except Exception:
		await message.reply("Invalid ID")
		return

	start_link = await client.ask(user_id, "Send me the link of message from where you want to start forwarding")
		
	try:
		start_link = start_link.text
		start_link = start_link.split("//")[1]
		start_link = start_link.split("/")
		source = int(start_link[2])
		source_id = int("-100"+ start_link[2])
		start_id = int(start_link[3])
		if target_id == source_id:
			await message.reply_text("Target Channel and Source Channel must be different")
			return 
	except Exception as e:
		await message.reply("Invalid ID")
		return

		
	end = await client.ask(user_id, "Send me the number of messages you want to forward")

	try:
		end = int(end.text)
				
	except Exception as e:
		await message.reply("No. of messages you want to forward must be an integer")
		return

	if user_id not in ADMINS:

		if await get_tasks() > 25:
			await message.reply("A maximum of 25 forward tasks can be run in the bot at time due to telegram restrictions\nPlease wait for some other task to end")
			return

		if await is_task(user_id):
			await message.reply("You are already running one task\nPlease wait for it to complete")
			return


	await add_task(user_id, source_id, target_id)

	end_id = start_id + end

	ist = dt.datetime.now(pytz.timezone('Asia/Kolkata'))

	temp = await message.reply_text(f"Forwarding....\n\nExpected time: {ist + dt.timedelta(0, end*( timeout + 0.2 ))} IST")
	i = start_id


	while i<end_id:
		try:

			msg5 = await app.get_messages(source_id, i)

			try:

				await msg5.copy(target_id)


				await asyncio.sleep(timeout)

			except FloodWait as e:

				logger.error(f"Sleeping for {e.value} seconds")
				await temp.edit(f"Sleeping for {e.value} seconds in {i}th message")
				await asyncio.sleep(e.value)
				await msg5.copy(target_id)
				await asyncio.sleep(timeout)

		except ChannelInvalid or ChatAdminRequired or PeerIdInvalid or KeyError or ValueError:

			await temp.delete()
			await message.reply_text("Make sure the bot is admin in both the channels where you want to forward and the source channel", reply_markup = error_markup)
			await del_task(user_id)
			return 

		except MessageEmpty:
			pass

		except RPCError as e:

			await temp.delete()
			logger.error(e)
			await message.reply_text("RPC Error Occurred\n\nMake sure the bot is admin in both the channels where you want to forward and the source channel\n\nIf you believe that you did everything correct, then report the error", reply_markup = error_markup)
			await del_task(user_id)
			return 

		except Exception as e:

			logger.error(e)
			await temp.delete()
			await message.reply_text(f"{e}\n\nThis error occurred in forwarding \nhttps://t.me/c/{source}/{i}", reply_markup = error_markup)
			await del_task(user_id)
			return 

		i+=1
	await temp.delete()
	await del_task(user_id)
	await message.reply_text(f"Done forwarding {end_id - start_id} messages")
			
@app.on_message(filters.command('start'))
async def start(client, message):

	if await is_banned_user(message.from_user.id):
		return None
	await add_user(message.from_user.id, message.from_user.first_name)

	await message.reply_text(f"Hello {message.from_user.first_name} \n\nI am the Manager of The Quantum\n\nCurrently forward feature is available for public\nYou can use it by /forward\n\nNote: Before Forwarding Make sure the bot is admin in both the channels where you want to forward and the source channel", reply_markup=start_markup)

@app.on_callback_query()
async def answer(client, query):
	if query.data == "help":
		await query.edit_message_text("Getting channel/group id \n\nCopy the link of any message of that channel/group\nFor example we take this link\n``https://t.me/c/1628389514/6746``\n\n1628389514 This is the channel/group id\n\nNote: Before Forwarding Make sure the bot is admin in both the channels where you want to forward and the source channel", reply_markup = back_markup )
		return
	if query.data == "back":
		await query.edit_message_text(f"Hello {query.from_user.first_name} \n\nI am the Manager of The Quantum\n\nCurrently forward feature is available for public\nYou can use it by /forward\n\nNote: Before Forwarding Make sure the bot is admin in both the channels where you want to forward and the source channel", reply_markup=start_markup)

@app.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban(client, message):
	try:
		id = int(message.text.split(" ")[1])
		await ban_user(id)
		await message.reply(f"Succesfully banned {id}")
	except Exception as e:
		logger.error(e)
		await message.reply_text("Please send in this format\n\n/ban user_id")

@app.on_message(filters.command('unban') & filters.user(ADMINS))
async def ban(client, message):
	try:
		id = int(message.text.split(" ")[1])
		await unban_user(id)
		await message.reply(f"Succesfully unbanned {id}")
	except Exception as e:
		logger.error(e)
		await message.reply_text("Please send in this format\n\n/unban user_id")

@app.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(client, message):
	logger.info("stats")
	nban = await get_nObanned()
	raw_uptime = dt.datetime.now() - start_time
	uptime = get_readable_time(raw_uptime.seconds)
	nusers = await get_nO_Users()
	tasks = await get_tasks()
	logger.info("stats2")

	await message.reply_text(f"Statisics of bot\n\nUsers: {nusers}\nBanned Users: {nban}\nTasks Running: {tasks}\n\nUptime: {uptime}")

@app.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def broadcast(client, message):
	if message.reply_to_message:
		query = await full_userbase()
		broadcast_msg = message.reply_to_message
		total = 0
		successful = 0
		blocked = 0
		deleted = 0
		unsuccessful = 0
		
		pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
		for chat_id in query:
			try:
				await broadcast_msg.copy(chat_id)
				successful += 1
			except FloodWait as e:
				await asyncio.sleep(e.x)
				await broadcast_msg.copy(chat_id)
				successful += 1
			except UserIsBlocked:
				await del_user(chat_id)
				blocked += 1
			except InputUserDeactivated:
				await del_user(chat_id)
				deleted += 1
			except:
				unsuccessful += 1
				pass
			total += 1
		
		status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
		
		return await pls_wait.edit(status)

	else:
		msg = await message.reply("""<code>Use this command as a replay to any telegram message with out any spaces.</code>""")
		await asyncio.sleep(8)
		await msg.delete()


@app.on_message(filters.command('temp'))
def temp(client, message):
	print(message.entities)


if __name__ == "__main__":
	app.run(del_all_tasks())
	app.run()

