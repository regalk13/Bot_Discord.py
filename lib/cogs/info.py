from datetime import datetime
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="userinfo", alisases=["ui"])
    async def userinfo(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        embed = Embed(title="Info Usuario",
                      colour=target.colour,
                      timestamp=datetime.utcnow())

        embed.set_thumbnail(url=target.avatar_url)

        fields = [("Nombre", str(target), True),
                  ("ID", target.id, True),
                  ("Bot", target.bot, True),
                  ("Top Role", target.top_role.mention, True),
                  ("Status", str(target.status).title(), True),
                  ("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
                  ("Creación", target.created_at.strftime("%d/%m/%Y %H/:%M:%S"), True),
                  ("Ingresó", target.joined_at.strftime("%d/%m/%Y %H/:%M:%S"), True),
                  ("Boosted", bool(target.premium_since),True)]
        
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name="serverinfo", aliases=["guildinfo"])
    async def serverinfo(self, ctx):
        embed = Embed(title="Server information",
                colour=ctx.guild.owner.colour,
                timestamp=datetime.utcnow())

        embed.set_thumbnail(url=ctx.guild.icon_url)

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
				    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
				    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
				    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, True),
				  ("Owner", ctx.guild.owner, True),
				  ("Región", ctx.guild.region, True),
				  ("Creación", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Miembros", len(ctx.guild.members), True),
				  ("Personas", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
				  ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
				  ("Miembros baneados", len(await ctx.guild.bans()), True),
				  ("Estados", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
				  ("Canales de texto", len(ctx.guild.text_channels), True),
				  ("Canales de voz", len(ctx.guild.voice_channels), True),
				  ("Categorías", len(ctx.guild.categories), True),
				  ("Roles", len(ctx.guild.roles), True),
				  ("Invitaciones", len(await ctx.guild.invites()), True),
				  ("\u200b", "\u200b", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("info")

def setup(bot):
    bot.add_cog(Info(bot))
