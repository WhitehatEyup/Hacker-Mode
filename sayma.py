import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, time

# -------------------- BOT AYARLARI --------------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------- JSON AYARLARI --------------------
JSON_FILE = "egitim.json"

try:
    with open(JSON_FILE, "r") as f:
        egitim_data = json.load(f)
except FileNotFoundError:
    egitim_data = {"total": 0, "today": 0, "counted_messages": []}
    with open(JSON_FILE, "w") as f:
        json.dump(egitim_data, f)

# -------------------- KANAL & ROL AYARI --------------------
LOGS_CHANNEL_ID = 1423703146496000082        # Gün sonu raporunun atılacağı kanal
EGITIM_LOG_CHANNEL_ID = 1262732721378033694  # Eğitim loglarının bulunduğu kanal

# Sadece bu iki rolün log mesajları sayılır
COUNTED_ROLES = [1122659508045496451,1122659625783803975]  # Ordu Subayı ve Üst Ordu Subayı rol ID'leri

START_TIME = time(0, 0)  # Bot açıldığında eski mesajları tararken 08:00 sonrası

# -------------------- ESKİ MESAJLARI SAY --------------------
async def eski_mesajlari_say():
    channel = bot.get_channel(EGITIM_LOG_CHANNEL_ID)
    if not channel:
        return
    
    guild = channel.guild  # Kanalın sunucusunu al
    async for message in channel.history(limit=None):
        if message.id not in egitim_data["counted_messages"]:
            member = guild.get_member(message.author.id)  # Author'u Member olarak al
            if member:  # Sunucuda hala varsa
                if any(role.id in COUNTED_ROLES for role in member.roles):
                    if message.created_at.time() >= START_TIME:
                        egitim_data["total"] += 1
                        egitim_data["today"] += 1
                        egitim_data["counted_messages"].append(message.id)

    with open(JSON_FILE, "w") as f:
        json.dump(egitim_data, f)


# -------------------- REAKSİYON İLE SAYIM --------------------
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.channel.id != EGITIM_LOG_CHANNEL_ID:
        return

    if str(reaction.emoji) == "✅":
        if any(role.id in COUNTED_ROLES for role in reaction.message.author.roles):
            message_id = reaction.message.id
            if message_id not in egitim_data["counted_messages"]:
                egitim_data["total"] += 1
                egitim_data["today"] += 1
                egitim_data["counted_messages"].append(message_id)

                with open(JSON_FILE, "w") as f:
                    json.dump(egitim_data, f)

# -------------------- GÜN SONU RAPORU --------------------
@tasks.loop(minutes=1)
async def gun_sonu_raporu():
    now = datetime.now()
    # 23:59 veya sonrasında raporu at
    if now.hour == 23 and now.minute >= 59:
        channel = bot.get_channel(LOGS_CHANNEL_ID)
        if channel:
            await channel.send(
                f"Gün sonu raporu:\n"
                f"Bugün toplam {egitim_data['today']} eğitim yapıldı.\n"
                f"Toplam eğitim sayısı: {egitim_data['total']}"
            )
        egitim_data["today"] = 0
        egitim_data["counted_messages"] = []
        with open(JSON_FILE, "w") as f:
            json.dump(egitim_data, f)

# -------------------- BOT HAZIR --------------------
@bot.event
async def on_ready():
    print(f"{bot.user} hazır!")
    await eski_mesajlari_say()  # Bot açıldığında eski 08:00 sonrası mesajları say
    gun_sonu_raporu.start()

# -------------------- BOTU ÇALIŞTIR --------------------
bot.run("")
