import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import random
import aiohttp

with open("Data/Wouter_Quirks.txt", "r", encoding="utf-8") as f:
    friend_messages = [line.strip() for line in f if line.strip()]
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def ask(ctx, *, question):
    style_examples = random.sample(friend_messages, k=min(5, len(friend_messages)))
    style_text = "\n".join(style_examples)

    payload = {
        "model": "openai/gpt-oss-20b", 
        "messages": [
            {"role": "system", "content": f"You are Wouter. Answer questions factually but in the style of these messages:\n{style_text}"},
            {"role": "user", "content": question}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_base}/chat/completions", json=payload, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                await ctx.send(f"Error from Groq API: {resp.status} — {text}")
                return
            data = await resp.json()
            answer = data["choices"][0]["message"]["content"]
            await ctx.send(answer)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot.run(BOT_TOKEN)