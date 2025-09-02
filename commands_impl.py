# commands_impl.py（或就放在同一檔案頂部也可）
import discord
from discord.ext import commands

@commands.command(name="ping")
async def ping_command(ctx: commands.Context):
    latency = round(ctx.bot.latency * 1000)
    await ctx.send(f"🏓 Pong! 延遲: {latency}ms")

@commands.command(name="status")
async def status_command(ctx: commands.Context):
    bot = ctx.bot
    embed = discord.Embed(title="🤖 Bot 狀態", color=0x00ff00)
    embed.add_field(name="延遲", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="伺服器數", value=len(bot.guilds), inline=True)

    # 你之前的 uptime 建議改成在 on_ready 設一個 started_at
    started_at = getattr(bot, "started_at", None)
    if started_at:
        embed.add_field(name="上線時間", value=f"<t:{int(started_at.timestamp())}:R>", inline=True)

    await ctx.send(embed=embed)

@commands.command(name="servers")
async def servers_command(ctx: commands.Context):
    embed = discord.Embed(title="📋 已連接的伺服器", color=0x0099ff)
    for guild in ctx.bot.guilds[:10]:
        embed.add_field(
            name=guild.name,
            value=f"ID: {guild.id}\n成員: {guild.member_count}\n頻道: {len(guild.channels)}",
            inline=True
        )
    if len(ctx.bot.guilds) > 10:
        embed.set_footer(text="只顯示前 10 個伺服器")
    await ctx.send(embed=embed)

@commands.command(name="channels")
async def channels_command(ctx: commands.Context):
    if not ctx.guild:
        await ctx.send("此命令只能在伺服器中使用")
        return
    embed = discord.Embed(title=f"📺 {ctx.guild.name} 的頻道", color=0x0099ff)
    text_channels = [ch for ch in ctx.guild.channels if isinstance(ch, discord.TextChannel)]
    voice_channels = [ch for ch in ctx.guild.channels if isinstance(ch, discord.VoiceChannel)]
    embed.add_field(name="文字頻道", value="\n".join([f"#{ch.name}" for ch in text_channels[:10]]) or "（無）", inline=True)
    embed.add_field(name="語音頻道", value="\n".join([f"🔊 {ch.name}" for ch in voice_channels[:10]]) or "（無）", inline=True)
    if len(text_channels) > 10 or len(voice_channels) > 10:
        embed.set_footer(text="只顯示前 10 個頻道")
    await ctx.send(embed=embed)