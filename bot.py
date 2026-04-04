import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Ayarlar
TOKEN = os.getenv("DISCORD_TOKEN")
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]

# Hafıza (Cezalar)
cezalar = {}

# Yetkiler
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.message_content = True
intents.members = True # Üye hareketlerini görmek için şart

client = discord.Client(intents=intents)

async def log_gonder(guild, mesaj):
    """Mesajı 'cellat-log' isimli kanala gönderir."""
    kanal = discord.utils.get(guild.text_channels, name="cellat-log")
    if kanal:
        try: await kanal.send(mesaj)
        except: pass

async def sese_baglan(guild):
    """Botu sunucudaki ilk uygun ses kanalına sokar."""
    if guild.voice_client and guild.voice_client.is_connected():
        return # Zaten seste, dokunma.

    for channel in guild.voice_channels:
        if channel.permissions_for(guild.me).connect:
            try:
                await channel.connect()
                print(f'🛡️ [SES] {guild.name} sunucusunda {channel.name} odasına pusu atıldı.')
                return True
            except:
                continue
    return False

@client.event
async def on_ready():
    print(f'✅ Bot Aktif: {client.user}')
    print(f'👑 Yetkililer: {ADMIN_IDS}')
    
    for guild in client.guilds:
        await sese_baglan(guild)
        await asyncio.sleep(1)

@client.event
async def on_guild_join(guild):
    print(f'🆕 Yeni Sunucu: {guild.name}')
    await asyncio.sleep(2)
    await sese_baglan(guild)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 1. CEZA KONTROLÜ (Otomatik Mesaj İşlemleri)
    if message.author.id in cezalar:
        ceza = cezalar[message.author.id]
        if ceza in ['end', 'chat']:
            try: await message.delete()
            except: pass
        elif ceza == 'mal':
            try:
                for r in ["🇲", "🇦", "🇱"]: await message.add_reaction(r)
            except: pass

    # 2. KOMUT KONTROLÜ (Sadece Adminler)
    if message.author.id not in ADMIN_IDS:
        return

    parts = message.content.split(' ')
    komut = parts[0].lower()

    # Liste Komutu
    if komut == '.liste':
        if not cezalar:
            await message.reply('📭 Aktif ceza yok.')
        else:
            txt = "**📜 Cezalılar:**\n" + "\n".join([f"• <@{u}>: `{c}`" for u, c in cezalar.items()])
            await message.reply(txt)
        return

    # Ceza Verme/Kaldırma Komutları
    if len(parts) >= 2:
        try:
            target_id = int(parts[1].strip())
        except:
            return

        # Af Komutu
        if komut == '.cikar':
            if target_id in cezalar:
                del cezalar[target_id]
                await message.reply(f'🔓 <@{target_id}> için tüm engeller kaldırıldı.')
                # Sesteyse susturmasını aç
                for g in client.guilds:
                    m = g.get_member(target_id)
                    if m and m.voice:
                        try: await m.edit(mute=False, deafen=False)
                        except: pass
            return

            return

        # Ceza Atama
        ceza_tipleri = {'.end': 'end', '.ses': 'ses', '.kulak': 'kulak', '.mal': 'mal', '.chat': 'chat'}
        if komut in ceza_tipleri:
            cezalar[target_id] = ceza_tipleri[komut]
            await message.reply(f'🔒 <@{target_id}> için `{ceza_tipleri[komut].upper()}` cezası aktif edildi.')
            
            # Anlık Operasyon (Sesteyse vur)
            for g in client.guilds:
                m = g.get_member(target_id)
                if m and m.voice:
                    try:
                        if komut in ['.end', '.ses']:
                            await m.edit(mute=True, deafen=True)
                            await m.move_to(None)
                        elif komut == '.kulak':
                            await m.edit(mute=True, deafen=True)
                    except: pass

@client.event
async def on_member_join(member):
    """Üye sunucuya katıldığında çalışır."""
    await log_gonder(member.guild, f'📥 **{member.name}** ({member.id}) sunucuya girdi.')

@client.event
async def on_member_remove(member):
    """Üye sunucudan çıktığında çalışır."""
    await log_gonder(member.guild, f'📤 **{member.name}** ({member.id}) sunucudan çıktı.')

@client.event
async def on_voice_state_update(member, before, after):
    # BOT KORUMASI: Bot odadan atılırsa geri girer
    if member.id == client.user.id and after.channel is None:
        print(f"⚠️ Bot atıldı, 5 saniye sonra geri sızıyor...")
        await asyncio.sleep(5)
        await sese_baglan(before.channel.guild)
        return

    # CEZA KONTROLÜ: Cezalı biri sese girerse veya susturmasını açarsa vur
    if member.id in cezalar:
        ceza = cezalar[member.id]
        if after.channel is not None:
            # Kaçmaya veya susturma açmaya çalışıyor mu?
            if ceza in ['end', 'ses']:
                try:
                    await member.edit(mute=True, deafen=True)
                    await member.move_to(None)
                    print(f'⚡ {member.name} seste yakalandı ve paketlendi.')
                except: pass
            elif ceza == 'kulak':
                if not after.mute or not after.deaf:
                    try: await member.edit(mute=True, deafen=True)
                    except: pass

client.run(TOKEN)
