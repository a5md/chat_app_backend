import asyncio 
import traceback
import json
from .database.redis_db import redis_client , init_redis , close_redis
from .services.email_service import Email_sender
import smtplib

email_sender = Email_sender()

async def worker():
    try:
        await init_redis()
        email_sender.connect()
        print("is running")
        while True:

            try:

                # Wait here until a job arrives
                _, payload = await redis_client.blpop("email_queue", timeout=0) #worker is sleeping until email job arrives
                print("send")
                job = json.loads(payload)

                try:
                    email_sender.send(job)

                except smtplib.SMTPServerDisconnected:
                    email_sender.connect()  # reconnect
                    email_sender.send(job)  # retry once
                

            except Exception as e:
                traceback.print_exc()
                await asyncio.sleep(5)

    finally:

        await close_redis()
        email_sender.close()
        print("is close")


if __name__ == "__main__":
    asyncio.run(worker())