from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from datetime import datetime, timedelta
from discord import Embed

from ..db import db

#numbers
#0⃣ 1️⃣ 2⃣ 3⃣ 4⃣ 5⃣ 6⃣ 7⃣ 8⃣ 9⃣

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = []
    
    @Cog.listener()
    async def on_ready(self):
	       if not self.bot.ready:
                self.colours = {
                    "❤️": self.bot.guild.get_role(766074172585017384),       #red
                    "💛": self.bot.guild.get_role(766075992111448074),       #yellow
                    "🧡": self.bot.guild.get_role(766074278625673236),       #orange
                    "💚": self.bot.guild.get_role(766074815496585237),       #gren
                    "💙": self.bot.guild.get_role(766074244253483038),       #blue
                    "💜": self.bot.guild.get_role(766074864628006942),       #purple
                    "🖤": self.bot.guild.get_role(66074510277345281),       #black
                }
                self.reaction_message = await self.bot.get_channel(766038079558516767).fetch_message(766089712573612083)
                self.bot.cogs_ready.ready_up("reactions")
                self.starboard_channel = self.bot.get_channel(766321103210938379)
    
    @command(name="createpoll", aliases=["mkpoll"])
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, hours: int, question: str, *options):
        await ctx.message.delete()
       
        if len(options) > 10:
            await ctx.send("La encuesta no puede tener más de 10 opciones.")
    
        else:
            embed = Embed(title="Encuesta",
                        description=question,
                        colour=ctx.author.colour,
                        timestamp=datetime.utcnow())
            
            fields = [("Opciones", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                    ("Instrucciones", "Reacciona y vota!", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            
            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)
            
            self.polls.append((message.channel.id, message.id))

            self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=hours),
									   args=[message.channel.id, message.id])

    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda  r: r.count)

        await message.channel.send(f"En la encuesta, la opción favorita fue {most_voted.emoji} con {most_voted.count-1:} votos!")
        self.polls.remove((message.channel.id, message.id))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours, reason="Color configurado.")
            await payload.member.add_roles(self.colours[payload.emoji.name], reason="Color configurado.")
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)
        
        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                    and payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)

        elif payload.emoji.name == "⭐":
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        
            if not message.author.bot:  #and payload.member.id != message.author.id:
                msg_id, stars = db.record("SELECT StartMessageID, Stars FROM starboard WHERE RootMessageID = ?", message.id) or (None, 0)
                
                embed = Embed(title="Starred message",
                              colour=message.author.colour,
                              timestamp=datetime.utcnow())
                
                fields = [("Autor ", message.author.mention, False),
                          ("Contenido", message.content or "Mira el post", False),
                          ("Estrellas", stars+1, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                if not stars:
                    star_message = await self.starboard_channel.send(embed=embed)
                    db.execute("INSERT INTO starboard (RootMessageID, StartMessageID) VALUES (?, ?)", message.id, star_message.id)
                
                else:
                    star_message = await self.starboard_channel.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?", message.id)

            else:
                await message.remove_reaction(payload.emoji, payload.member)

def setup(bot):
    bot.add_cog(Reactions(bot))