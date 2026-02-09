from dotenv import load_dotenv
import pytz
import os
import asyncio
from telegram import Bot
from datetime import datetime

load_dotenv()
TELEGRAM_TOKEN= os.getenv('TELEGRAM_TOKEN')
CHAT_ID= os.getenv('CHAT_ID')

async def send_poll_mor_aft ():

    bot = Bot(TELEGRAM_TOKEN)
    fuso_br = pytz.timezone('America/Sao_Paulo')
    today = datetime.now(fuso_br).strftime('%Y-%m-%d %H:%M')

    title = f"Meal Plan (Company) Morning and Afternoon - {today}"
    options = [
        '1 pote de iogurte grego 500ml', 
        '2 bananas',
        '4 colheres de granola (no pote)',
        '1 colher de pasta de amendoim'
            ]

    await bot.send_poll(
    chat_id=CHAT_ID, 
    question=title, 
    options=options, 
    is_anonymous=False, 
    allows_multiple_answers=True
    )

# secure execution
if __name__ == "__main__":
    asyncio.run(send_poll_mor_aft())