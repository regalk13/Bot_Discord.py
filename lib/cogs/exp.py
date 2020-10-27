from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Member, Embed
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len_data = len(self.entries)

        embed = Embed(tittle="Tabla de experiencia.",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} de {len_data:,} miembros.")

        for name, value in fields:
                embed.add_field(name=name, value=value, inline=False)

        return embed
    
    async def format_page(self, menu, entries):
        offset = (menu.current_page*self.per_page) + 1
        
        fields = []
        table = ("\n".join(f"{idx+offset}. {self.ctx.bot.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Level: {entry[2]})"
        for idx, entry in enumerate(entries)))

        fields.append(("Ranks", table))
        
        return await self.write_page(menu, offset, fields)

class Exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id) 

        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_to_add = randint(10, 20)
        new_lvl = int(((xp+xp_to_add)//42) ** 0.55)
        
        db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
                   xp_to_add, new_lvl, (datetime.utcnow()+timedelta(seconds=60)).isoformat(), message.author.id)
        
        if new_lvl > lvl:
            await self.levelup_channel.send(f"Felicidades {message.author.mention} has alcanzado el nivel {new_lvl:,}!")
    

    async def check_lvl_rewards(self, message, lvl):
        if lvl >= 50: # Mammut
            if (new_role := message.guild.get_role(766808210630901810)) not in message.author.roles:
                await message.author.add_roles(new_role)

        elif 40 <= lvl < 50: # Ninja
            if (new_role := message.guild.get_role(766808108877611029)) not in message.author.roles:
                await message.author.add_roles(new_role)

        elif 30 <= lvl < 40: # Master
            if (new_role := message.guild.get_role(766807991378640897)) not in message.author.roles:
                await message.author.add_roles(new_role)
	
        elif 20 <= lvl < 30: # Hechizero
            if (new_role := message.guild.get_role(766807888525393922)) not in message.author.roles:
                await message.author.add_roles(new_role)

        elif 10 <= lvl < 20: # Aprendiz
            if (new_role := message.guild.get_role(766807837618995251)) not in message.author.roles:
                await message.author.add_roles(new_role)
				
        elif 5 <= lvl < 9: # Beginner
            if (new_role := message.guild.get_role(766807774742446140)) not in message.author.roles:
                await message.author.add_roles(new_role)
    
    @command(name="level")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record("SELECT XP, level FROM exp WHERE UserID = ?", target.id) or (None, None)

        if lvl is not None:
            await ctx.send(f"{target.display_name} está en el nivel {lvl:,} con {xp:,} de experiencia.")

        else:
            await ctx.send("Este miembro no se encuentra en el sistema de niveles.")

    @command(name="rank")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM exp ORDER BY XP DESC")

        try:
            await ctx.send(f"{target.display_name} está en el puesto {ids.index(target.id)+1} de {len(ids)}")

        except ValueError:
            await ctx.send("Este miembro no se encuentra en el sistema de niveles.")

    @command(name="leaderboard", aliases=["lb"])
    async def display_leaderboard(self, ctx):
        records = db.records("SELECT UserID, XP, Level FROM exp ORDER BY XP DESC")
        
        menu = MenuPages(source=HelpMenu(ctx, records),
						 clear_reactions_after=True,
						 timeout=60.0)
		
        await menu.start(ctx)
    
    @Cog.listener()
    async def on_ready(self):
	    if not self.bot.ready:
               self.levelup_channel = self.bot.get_channel(766449343212421120)
               self.bot.cogs_ready.ready_up("exp")
    
    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message)

def setup(bot):
    bot.add_cog(Exp(bot))
