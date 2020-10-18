from datetime import datetime, timedelta
from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from discord import Activity, ActivityType
from apscheduler.triggers.cron import CronTrigger
from time import time
from psutil import Process, virtual_memory
from discord import __version__ as discord_version
from platform import python_version

class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "Watching >help | Mi DM para ModMail."

        bot.scheduler.add_job(self.set, CronTrigger(second=0))
    
    @property
    def message(self):
        return self._message.format(users=len(self.bot.users), guilds=len(self.bot.guilds))
    
    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Esta actividad no existe.")

        self._message = value
    
    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.bot.change_presence(activity=Activity(
            name=_name, type=getattr(ActivityType, _type, ActivityType.playing)
        ))
    
    @command(name="setactivity")
    @has_permissions(manage_guild=True)
    async def set_activity_message(self, ctx, *, text: str):
        self.message = text
        await self.set()

    @command(name="ping")
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(f"Pong! latencia: {self.bot.latency*1000:,.0f} ms.") 
        end = time()

        await message.edit(content=f"Pong! latencia: {self.bot.latency*1000:,.0f} ms, tiempo de respuesta: {(end-start)*1000:,.0f} ms.")
    
    @command(name="stats")
    async def show_bot_stats(self, ctx):
        embed = Embed(title="Bot stats",
                      colour=ctx.author.colour,
                      timestamp=datetime.utcnow())

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time()-proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024**2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("Bot version", self.bot.VERSION, True),
            ("Python version", python_version(), True),
            ("discord.py version", discord_version, True),
            ("Uptime", uptime, True),
            ("CPU", cpu_time, True),
            ("Memoria usada", f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:.0f}%)", True),
            ("Usuarios", f"{self.bot.guild.member_count:,}", True)
		]
        
        
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text="Creador Regalk13.")

        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
               self.bot.cogs_ready.ready_up("meta")


def setup(bot):
    bot.add_cog(Meta(bot))