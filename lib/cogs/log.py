from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command


class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
                embed = Embed(title="Actualización de nombre",
                              colour=after.colour,
                              timestamp=datetime.utcnow())

                fields = [("Antes", before.name, False),
                          ("Despues", after.name, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

        if before.name != after.name:
                embed = Embed(title="Actualización de Tag",
                              colour=after.colour,
                              timestamp=datetime.utcnow())

                fields = [("Antes", before.discriminator, False),
                          ("Despues", after.discriminator, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Actualización Miembro",
                          description="Avatar cambiado (La imagen de abajo es la nueva, la antigua la de la derecha).",
                          colour=self.log_channel.guild.get_member(after.id).colour,
                          timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            embed = Embed(title="Actualización Miembro",
                          description="Nickname cambiado",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            fields = [("Antes", before.display_name, False),
                      ("Despues", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

        elif before.roles != after.roles:
            embed = Embed(title="Actualización Miembro",
                          description=f"Actualización de roles de {after.display_name}",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            fields = [("Antes", ", ".join([r.mention for r in before.roles[:1]]), False),
                      ("Despues", ", ".join([r.mention for r in after.roles[:1]]), False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                embed = Embed(title="Edición de mensaje.",
                              description=f"Editado por {after.author.display_name}",
                              colour=after.author.colour,
                              timestamp=datetime.utcnow())

                fields = [("Antes", before.content, False),
                          ("Despues", after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.log_channel.send(embed=embed)


    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            embed = Embed(title="Mensaje borrado.",
                          description=f"mensaje borrado por {message.author.display_name}",
                          colour=message.author.colour,
                          timestamp=datetime.utcnow())

            fields = [("Contenido", message.content, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await self.log_channel.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
	       if not self.bot.ready:
                  self.log_channel = self.bot.get_channel(764255491680632842)
                  self.bot.cogs_ready.ready_up("log")

def setup(bot):
    bot.add_cog(Log(bot))
