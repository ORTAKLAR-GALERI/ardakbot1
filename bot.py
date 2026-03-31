import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]

cezalar = {}

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.message_content = True

client = discord.Client(intents=intents)

async def sese_baglan(guild):
    """Bulunulan sunucuda uygun bir ses kanalına bağlanır."""
    for channel in guild.voice_channels:
        if channel.permissions_for(guild.me).connect:
            try:
                # Eğer zaten bağlıysa önce bağlantıyı kes (nadiren gerekebilir)
                if guild.voice_client:
                    await guild.voice_client.disconnect(force=True)
                
                await channel.connect()
                print(f'🏕️ [OTO-SES] {guild.name} sunucusunda {channel.name} odasına sessiz koruma kalkanı atıldı.')
                return True
            except Exception as e:
                print(f'❌ [OTO-SES HATA] {guild.name} sunucusunda sese girilemedi: {e}')
    return False

@client.event
async def on_ready():
    print(f'🤖 Bot başarıyla giriş yaptı: {client.user}')
    print(f'👑 Yönetici ID(ler): {ADMIN_IDS}')
    print('📡 Gelişmiş Ceza Sistemi Devrede. Mesajlar ve Ses dinleniyor...')

    for guild in client.guilds:
        await sese_baglan(guild)
        await asyncio.sleep(1.5) # Aşırı yüklenmeyi önlemek için kısa bekleme

@client.event
async def on_guild_join(guild):
    print(f'🆕 Yeni bir sunucuya katıldım: {guild.name} (ID: {guild.id})')
    # Sunucuya yeni katıldığında sese girmek için kısa bir süre bekle (yetkilerin oturması için)
    await asyncio.sleep(2)
    await sese_baglan(guild)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Ceza kontrolü (Mesaj silme/emoji)
    if message.author.id in cezalar:
        ceza = cezalar[message.author.id]
        if ceza in ['end', 'chat']:
            try:
                await message.delete()
            except discord.Forbidden:
                print(f'❌ Hata: {message.author} mesajını silmeye yetki yetmedi!')
            except discord.NotFound:
                pass
        elif ceza == 'mal':
            try:
                await message.add_reaction("🇲")
                await message.add_reaction("🇦")
                await message.add_reaction("🇱")
            except discord.Forbidden:
                print(f'❌ Hata: {message.author} kişisinin mesajına emoji koymak için yetki yetmedi!')
            except discord.NotFound:
                pass

    if message.author.id not in ADMIN_IDS:
        return

    parts = message.content.split(' ')
    komut = parts[0].lower()

    if komut == '.liste':
        if not cezalar:
            await message.reply('📭 Şu an kimsenin aktif cezası bulunmuyor.')
        else:
            liste_metni = "**📜 Aktif Cezalılar Listesi:**\n"
            for u_id, c_tip in cezalar.items():
                liste_metni += f"• <@{u_id}>: `{c_tip.upper()}`\n"
            await message.reply(liste_metni)
        return

    if len(parts) >= 2:
        try:
            hedef_id = int(parts[1].strip())
        except ValueError:
            if komut in ['.end', '.ses', '.kulak', '.mal', '.chat', '.cikar']:
                await message.reply('❌ Lütfen geçerli bir ID girin. (Örn: `.end 123456789`)')
            return

        if komut in ['.end', '.ses', '.kulak', '.mal', '.chat']:
            if komut == '.end':
                cezalar[hedef_id] = 'end'
                await message.reply(f'🧨 `{hedef_id}` kişisine **END** cezası verildi!')
                print(f"🔒 [CEZA] 'END' - Veren: {message.author} | Hedef: {hedef_id}")
            elif komut == '.ses':
                cezalar[hedef_id] = 'ses'
                await message.reply(f'🎵 `{hedef_id}` kişisine **SES** cezası verildi!')
                print(f"🔒 [CEZA] 'SES' - Veren: {message.author} | Hedef: {hedef_id}")
            elif komut == '.kulak':
                cezalar[hedef_id] = 'kulak'
                await message.reply(f'🎧 `{hedef_id}` kişisine **KULAK** cezası verildi!')
                print(f"🔒 [CEZA] 'KULAK' - Veren: {message.author} | Hedef: {hedef_id}")
            elif komut == '.mal':
                cezalar[hedef_id] = 'mal'
                await message.reply(f'🤡 `{hedef_id}` kişisine **MAL** cezası verildi!')
                print(f"🔒 [CEZA] 'MAL' - Veren: {message.author} | Hedef: {hedef_id}")
            elif komut == '.chat':
                cezalar[hedef_id] = 'chat'
                await message.reply(f'🙊 `{hedef_id}` kişisine **CHAT** cezası verildi!')
                print(f"🔒 [CEZA] 'CHAT' - Veren: {message.author} | Hedef: {hedef_id}")

            for guild in client.guilds:
                member = guild.get_member(hedef_id)
                if member and member.voice and member.voice.channel:
                    try:
                        if komut in ['.end', '.ses']:
                            await member.edit(mute=True, deafen=True)
                            await member.move_to(None)
                            print(f'⚡ AKTİF OPERASYON: {member.name} seste yakalandı ve havada vuruldu!')
                        elif komut == '.kulak':
                            await member.edit(mute=True, deafen=True)
                            print(f'⚡ AKTİF OPERASYON: {member.name} seste sohbetin ortasında kör ve sağır bırakıldı!')
                    except Exception as e:
                        print(f'❌ Aktif Operasyon Başarısız: {e}')
        elif komut == '.cikar':
            if hedef_id in cezalar:
                del cezalar[hedef_id]
                await message.reply(f'🗑️ `{hedef_id}` kişinin tüm cezaları kaldırıldı.')
                print(f"🔓 [AF] Ceza kaldırıldı: {hedef_id}")

                for guild in client.guilds:
                    member = guild.get_member(hedef_id)
                    if member and member.voice and member.voice.channel:
                        try:
                            await member.edit(mute=False, deafen=False)
                            print(f'✅ {member.name} üzerindeki sesli engeller tamamen kaldırıldı.')
                        except Exception as e:
                            print(f'❌ {member.name} engelleri kaldırılırken hata oldu: {e}')
            else:
                await message.reply('⚠️ Bu kişi zaten cezalı bulunmuyor.')

@client.event
async def on_voice_state_update(member, before, after):
    if member.id == client.user.id and before.channel is not None and after.channel is None:
        print(f"⚠️ İMDAT! Bot odadan atıldı! İnadına tekrar sessizce sese sızılıyor...")
        guild = before.channel.guild
        
        async def inatci_ziplama():
            await asyncio.sleep(2)
            if guild.voice_client:
                await guild.voice_client.disconnect(force=True)
                
            for channel in guild.voice_channels:
                if channel.permissions_for(guild.me).connect:
                    try:
                        vc = await channel.connect()
                        print(f'🛡️ [İNATÇI-SES] Saniyesinde {channel.name} adlı sese sessiz koruma için intikal edildi.')
                        break
                    except:
                        pass
        
        client.loop.create_task(inatci_ziplama())
        return

    if member.id in cezalar:
        ceza_tipi = cezalar[member.id]
        if after.channel is not None:
            if before.channel != after.channel or not after.mute or not after.deaf:
                print(f'\n🚨 CEZALI HAREKETİ YAKALANDI! Sürüm: {ceza_tipi.upper()} | Kullanıcı: ({member})')
                try:
                    if ceza_tipi in ['end', 'ses']:
                        if not after.mute or not after.deaf:
                            await member.edit(mute=True, deafen=True)
                        await member.move_to(None)
                        print(f'✅ {member} sesten ATAK YEDİ.')
                    elif ceza_tipi == 'kulak':
                        if not after.mute or not after.deaf:
                            await member.edit(mute=True, deafen=True)
                            print(f'✅ {member} kulaklığını açmaya çalıştı, saniyesinde geri kapatıldı!')
                except discord.Forbidden:
                    print(f'❌ Yetki hatası: Botun yetkileri eksik!')
                except Exception as e:
                    print(f'❌ Hata: {e}')
    else:
        if after.channel is not None and before.channel != after.channel:
            print(f'👀 Biri sese girdi: {member} | ID: {member.id}')

client.run(TOKEN)
