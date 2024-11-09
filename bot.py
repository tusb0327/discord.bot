import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime

# 외부 파일에서 토큰을 읽어오기
with open(r'C:\Users\tusb0\OneDrive\바탕 화면\log\토큰.txt', 'r') as file:
    TOKEN = file.read().strip()

VOICE_CHANNEL_ID = 1304761876848181289
direct_channel_id = 1300127710844031128
admin_action_channel_id = 1302300509549625364

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

@tasks.loop(seconds=60)
async def update_channel_name():
    guild = bot.guilds[0]
    await update_voice_channel_name(guild)

async def update_voice_channel_name(guild):
    voice_channel = guild.get_channel(VOICE_CHANNEL_ID)
    if voice_channel:
        total_member_count = sum(len(channel.members) for channel in guild.voice_channels)
        new_name = f"음성 인원 : {total_member_count}"

        if voice_channel.name != new_name:
            await voice_channel.edit(name=new_name)
            print(f"Updated channel name to: {new_name}")

@bot.event
async def on_ready():
    print(f'{bot.user} 로 로그인되었습니다!')
    
    await update_voice_channel_name(bot.guilds[0])

    update_channel_name.start()

@bot.event
async def on_voice_state_update(member, before, after):
    direct_channel = bot.get_channel(direct_channel_id)
    admin_action_channel = bot.get_channel(admin_action_channel_id)

    current_time = datetime.now().strftime("오늘 오후 %I:%M")

    if before.channel is None and after.channel is not None:
        embed = discord.Embed(
            description=f"{member.mention} 음성 채널에 들어감 <#{after.channel.id}>",
            color=0x57F287
        )
        
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_author(name=member.display_name, icon_url=avatar_url)
        embed.set_footer(text=f"ID: {member.id} • {current_time}")
        
        await direct_channel.send(embed=embed)

    elif before.channel is not None and after.channel is None:
        embed = discord.Embed(
            description=f"{member.mention} 음성 채널에서 나옴 <#{before.channel.id}>",
            color=0xED4245
        )
        
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_author(name=member.display_name, icon_url=avatar_url)
        embed.set_footer(text=f"ID: {member.id} • {current_time}")
        
        await direct_channel.send(embed=embed)

    elif before.mute != after.mute or before.deaf != after.deaf:
        await asyncio.sleep(2)

        async for entry in member.guild.audit_logs(limit=5):
            if entry.target and entry.target.id == member.id and entry.user:
                action_user = entry.user.mention
                target_user = member.mention

                if entry.action == discord.AuditLogAction.member_update:
                    embed = discord.Embed(color=0x5865F2)
                    
                    if hasattr(entry.before, "mute") and hasattr(entry.after, "mute") and entry.before.mute != entry.after.mute:
                        if entry.after.mute:
                            embed.description = f"{action_user} 님이 {target_user} 님의 마이크를 음소거했습니다."
                        else:
                            embed.description = f"{action_user} 님이 {target_user} 님의 마이크 음소거를 해제했습니다."

                    if hasattr(entry.before, "deaf") and hasattr(entry.after, "deaf") and entry.before.deaf != entry.after.deaf:
                        if entry.after.deaf:
                            embed.description = f"{action_user} 님이 {target_user} 님의 헤드셋을 음소거했습니다."
                        else:
                            embed.description = f"{action_user} 님이 {target_user} 님의 헤드셋 음소거를 해제했습니다."
                    
                    embed.set_footer(text=f"ID: {member.id} • {current_time}")
                    await admin_action_channel.send(embed=embed)
                    break

bot.run(TOKEN)
