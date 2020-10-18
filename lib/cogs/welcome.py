from discord import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command

from ..db import db

class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member):
            db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
            await self.bot.get_channel(752951710346903694).send(f"Bienvenido@ a **{member.guild.name}** {member.mention}! Visita <#751428354086928464> y saluda a todos!")

            try:
                await member.send(f"Bienvenid@ a **{member.guild.name}**! disfruta tu estadía!, no olvides revisar las reglas para evitar problemas.")

            except Forbidden:
                pass

            await member.add_roles(member.guild.get_role(760567454275207209))     #member.guild.get_role(763812765751574528))

    @Cog.listener()
    async def on_member_remove(self, member):
	    db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
	    await self.bot.get_channel(762434670574567474).send(f"{member.display_name} ha dejado {member.guild.name}.")

    @Cog.listener()
    async def on_ready(self):
	       if not self.bot.ready:
                  self.bot.cogs_ready.ready_up("welcome")

def setup(bot):
    bot.add_cog(Welcome(bot))
