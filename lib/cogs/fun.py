import random
from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord.errors import HTTPException
from discord.ext.commands import Cog
from discord.ext.commands import BucketType
from discord.ext.commands import command, cooldown

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name= "8ball")
    async def _8ball(self, ctx, *, question):
        responses = ["Es cierto.",

                     "Es decididamente así.",

                     "Sin duda.",

                     "Sí definitivamente.",

                     "Puedes confiar en ello.",

                     "Como yo lo veo, sí.",

                     "Más probable.",

                     "Perspectivas buenas.",

                     "Si.",

                     "Las señales apuntan a que sí.",

                     "Respuesta confusa, intenta otra vez.",

                     "Pregunta de nuevo más tarde.",

                     "Mejor no decirte ahora.",

                     "No se puede predecir ahora.",

                     "Concéntrate y pregunta otra vez.",

                     "No cuentes con eso",

                     "Mi respuesta es no.",

                     "Mis fuentes dicen que no.",

                     "Outlook no es tan bueno",



                     "Muy dudoso."]
        await ctx.send(f"Pregunta: {question}\nRespuesta: {random.choice(responses)}")

    @command(name="fact")
    @cooldown(3, 60, BucketType.guild)
    async def animal_fact(self, ctx, animal: str):
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
                fact_url = f"https://some-random-api.ml/facts/{animal}"
                image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

                async with request("GET", image_url, headers={}) as response:
                    if response.status == 200:
                            data = await response.json()
                            image_link = data["link"]

                    else:
                            image_link = None

                async with request("GET", fact_url, headers={}) as response:
                    if response.status == 200:
                        data = await response.json()

                        embed = Embed(title=f"{animal.title()} fact",
                                      description=data["fact"],
                                      colour=ctx.author.colour)

                        if image_link is not None:
                            embed.set_image(url=image_link)

                        await ctx.send(embed=embed)

                    else:
                        await ctx.send(f"API returned a {response.status} status.")

        else:
                await ctx.send("No fact are aviable for that animal.")

    @command(name="slap", aliases=["hit"])
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "Ninguna razón"):
        await ctx.send(f"{ctx.author.mention} amonesto a {member.mention} por {reason}!")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("No puedo encontrar ese miembro.")

    @command(name="echo", aliases=["say"])
    @cooldown(1, 15, BucketType.guild)
    async def echo_message(self, ctx, *, message):
	    await ctx.message.delete()
	    await ctx.send(message)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
               self.bot.cogs_ready.ready_up("fun")

def setup(bot):
    bot.add_cog(Fun(bot))
