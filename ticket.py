import discord
from discord.ext import commands
from discord.ui import View, Button
import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Log kanalı adı
LOG_CHANNEL_NAME = "ticket-logs"

# 🎫 Ticket paneli komutu
@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="🎓 Akademi Başkanlığı Ticket Sistemi",
        description="Aşağıdaki butonlardan açmak istediğiniz ticket türünü seçin:",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Akademi işi, gönül işi!")

    view = TicketMenu(ctx.channel.category)
    await ctx.send(embed=embed, view=view)


# 🎛️ Ticket Buton Menüsü
class TicketMenu(View):
    def __init__(self, category):
        super().__init__(timeout=None)
        self.category = category  # Panelin kategorisini kaydet

    @discord.ui.button(label="📘 Eğitim", style=discord.ButtonStyle.primary)
    async def egitim(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "eğitim")

    @discord.ui.button(label="⚖️ Ceza / Ödül", style=discord.ButtonStyle.danger)
    async def ceza(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "ceza")

    @discord.ui.button(label="🪖 Terfi / Tenzil", style=discord.ButtonStyle.success)
    async def terfi(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "terfi")

    @discord.ui.button(label="⏰ Mazeret", style=discord.ButtonStyle.secondary)
    async def mazeret(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "mazeret")

    @discord.ui.button(label="❓ Genel Destek", style=discord.ButtonStyle.secondary)
    async def destek(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "destek")

    async def create_ticket(self, interaction: discord.Interaction, konu: str):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Ticket kanalı aç (panelin kategorisinde)
        ticket_kanal = await guild.create_text_channel(
            name=f"ticket-{konu}-{interaction.user.name}",
            overwrites=overwrites,
            category=self.category
        )

        # Ticket açılış embedi
        embed = discord.Embed(
            title=f"🎫 {konu.title()} Ticket",
            description=f"Merhaba {interaction.user.mention},\n"
                        f"Bu ticket {konu} başvurunuz için açıldı. Yetkililer yakında ilgilenecektir.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Akademi Başkanlığı")

        view = CloseButton()
        await ticket_kanal.send(embed=embed, view=view)

        await interaction.response.send_message(
            f"✅ Ticket açıldı: {ticket_kanal.mention}", ephemeral=True
        )

        # Ticket loglama
        log_kanal = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if log_kanal:
            await log_kanal.send(
                f"🎫 Ticket Açıldı | Tür: {konu.title()} | Açan: {interaction.user.mention} | Kanal: {ticket_kanal.mention} | Tarih: {datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M')}"
            )


# 🔒 Ticket Kapatma Butonu
class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Ticket Kapat", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: Button):
        log_kanal = discord.utils.get(interaction.guild.text_channels, name=LOG_CHANNEL_NAME)
        if log_kanal:
            await log_kanal.send(
                f"🔒 Ticket Kapatıldı | Kanal: {interaction.channel.name} | Kapatan: {interaction.user.mention} | Tarih: {datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M')}"
            )
        await interaction.channel.delete()


@bot.event
async def on_ready():
    print(f"✅ Bot aktif: {bot.user}")


bot.run("BURAYA_BOT_TOKEN")