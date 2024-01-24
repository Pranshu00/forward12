import motor.motor_asyncio
from config import DB_URI, DB_NAME
import datetime as dt

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
tasks = database['ongoing_task']
banned = database['banned_user']

async def present_user(user_id : int):
        found = await user_data.find_one({'_id': user_id})
        return bool(found)

async def add_user(user_id: int, name):
    if not await present_user(user_id):
        await user_data.insert_one({'_id': user_id, "name": name})

async def get_nO_Users():
    n = await user_data.count_documents({})
    return n

async def full_userbase():
    user_docs = user_data.find()
    user_docs2 = await user_docs.to_list(length = 10000)
    user_ids = []
    for doc in user_docs2:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    if await present_user(user_id):
        await user_data.delete_one({'_id': user_id})
    
async def is_banned_user(user_id : int):
    found = await banned.find_one({'_id': user_id})
    return bool(found)

async def ban_user(user_id: int):
    await del_user(user_id)
    if not bool(await banned.find_one({'_id': user_id})):
        await banned.insert_one({
            "_id": user_id
        })

async def unban_user(user_id: int):
    if bool(await banned.find_one({'_id': user_id})):
        await banned.delete_one({
            "_id": user_id
        })

async def get_banned():
    user_docs = await banned.find()
    return user_docs

async def get_nObanned():
    n = await banned.count_documents({})
    return n

async def add_task(user_id, source, target):
        await tasks.insert_one({
            "id": user_id,
            "start": dt.datetime.now(),
            "source": source,
            "target": target
        })

async def get_tasks():
    return await tasks.count_documents({})

async def is_task(user_id):
    task = await tasks.find_one({"id": user_id})
    return bool(task)

async def get_task(user_id):
    task = await tasks.find_one({"id": user_id})
    return task

async def del_task(user_id):
    await tasks.delete_one({'id': user_id})
    
    
async def del_all_tasks():
    await tasks.delete_many({})