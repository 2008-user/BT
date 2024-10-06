import aiosqlite
import datetime
from dateutil.relativedelta import relativedelta

DATABASE = 'tokens.db'

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                guid TEXT PRIMARY KEY,
                token TEXT UNIQUE,
                group_guid TEXT,
                activation_date TEXT
            )
        ''')
        await db.commit()

async def add_token(guid, token, group_guid):
    async with aiosqlite.connect(DATABASE) as db:
        activation_date = datetime.datetime.now()
        await db.execute('''
            INSERT INTO tokens (guid, token, group_guid, activation_date)
            VALUES (?, ?, ?, ?)
        ''', (guid, token, group_guid, activation_date.isoformat()))
        await db.commit()

async def check_token_expiration():
    async with aiosqlite.connect(DATABASE) as db:
        current_time = datetime.datetime.now()
        async with db.execute('SELECT guid, token, activation_date FROM tokens') as cursor:
            async for row in cursor:
                guid, token, activation_date = row
                activation_date = datetime.datetime.fromisoformat(activation_date)
                expiration_date = activation_date + relativedelta(days=30)
                
                if current_time >= expiration_date:
                    print(f"Token {token} for user {guid} has expired.")
                    # منقضی کردن توکن در اینجا می‌توانید انجام دهید

async def extend_token(guid):
    async with aiosqlite.connect(DATABASE) as db:
        current_time = datetime.datetime.now()
        new_activation_date = current_time.isoformat()
        await db.execute('''
            UPDATE tokens SET activation_date = ?
            WHERE guid = ?
        ''', (new_activation_date, guid))
        await db.commit()

async def delete_token(guid):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('DELETE FROM tokens WHERE guid = ?', (guid,))
        await db.commit()

async def get_all_tokens():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT * FROM tokens') as cursor:
            return await cursor.fetchall()

async def get_user_info(guid):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT * FROM tokens WHERE guid = ?', (guid,)) as cursor:
            row = await cursor.fetchone()
            if row:
                token, group_guid, activation_date = row[1], row[2], row[3]
                activation_date = datetime.datetime.fromisoformat(activation_date)
                expiration_date = activation_date + relativedelta(days=30)
                remaining_days = (expiration_date - datetime.datetime.now()).days
                return {
                    "remaining_days": remaining_days,
                    "activation_date": activation_date.strftime("%Y-%m-%d"),
                    "user_guid": guid,
                    "group_guid": group_guid,
                }
            return None

async def change_group_guid(guid, new_group_guid):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            UPDATE tokens SET group_guid = ?
            WHERE guid = ?
        ''', (new_group_guid, guid))
        await db.commit()


async def main():
    await init_db()
    await add_token("user_guid_1", "token_123", "group_guid_1")
    print(await get_user_info("user_guid_1"))
    await extend_token("user_guid_1")
    print(await get_all_tokens())
    await change_group_guid("user_guid_1", "new_group_guid")
    print(await get_user_info("user_guid_1"))
    

