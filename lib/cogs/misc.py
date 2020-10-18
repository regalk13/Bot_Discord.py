from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="prefix")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
            if len(new) > 5:
                    await ctx.send("El prefix no puede tener más de 5 carácteres.")

            else:
                    db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
                    await ctx.send(f"El prefix fue actualizado a {new}.")

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("No tienes permisos para esto.")

    @Cog.listener()
    async def on_ready(self):
	    if not self.bot.ready:
               self.bot.cogs_ready.ready_up("misc")

def setup(bot):
    bot.add_cog(Misc(bot))
