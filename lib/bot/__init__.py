import discord
from asyncio import sleep
from datetime import datetime
from glob import glob
import sqlite3

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import (CommandNotFound, BadArgument , MissingRequiredArgument, CommandOnCooldown, MissingPermissions)
from discord.ext.commands import when_mentioned_or, command, has_permissions
from pathlib import Path

from ..db import db

intents=discord.Intents.all()
OWNER_IDS = [751143350299787276]
COGS = [p.stem for p in Path(".").glob("./lib/cogs/*.py")] #The problem being the split("\\"). On linux paths are split with /, /path/to/file.
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	return when_mentioned_or(prefix)(bot, message)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=discord.Intents.all())
    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    
    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                    ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                    ((member.id,) for member in self.guild.members if not member.bot))
       
        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                    ((id_,) for id_ in to_remove))

        db.commit()

    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running BOT...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("No estoy listo para recibir mensajes.")


    async def rules_reminder(self):
        await self.channel.send("Recuerda las reglas del server, visita Reglas y leelas.")

    async def on_connect(self):
        print("bot connected")

    async def on_disconect(self):
        print("bot disconected")

    async def on_error(self, err, *arg, **kwargs):
        if err == "on_command_error":
            await arg[0].send("Tengo algún error.")


        await self.stdout.send("Ha ocurrido algún error")       
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, CommandNotFound):
            await ctx.send("Este comando no existe.")

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Algún o algunos argumentos faltan.")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"Toma un respiro e intenta de nuevo en {exc.retry_after:,.2f} segundos")

        elif isinstance(exc, MissingPermissions):
            await ctx.send("No tienes permisos para esto...")

        elif hasattr(exc, "original"):
            if isinstance(exc.original, HTTPException):
                await ctx.send("Inhabilitado para enviar mensajes.")

            if isinstance(exc.original, Forbidden):
                await ctx.send("No tengo permisos para eso.")

            else:
                raise exc.original


        else:
            raise exc


    async def on_ready(self):
         if not self.ready:
                self.guild = self.get_guild(751428354086928461)
                self.stdout = self.get_channel(762837811485212712)
                self.channel = self.get_channel(751428354086928464)
                self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
                self.scheduler.start()


                self.update_db()

                while not self.cogs_ready.all_ready():
                    await sleep(0.5)

                await self.stdout.send("Now online!")
                self.ready = True
                print("bot ready")

         else:
                print("bot reconnect")

    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if len(message.content) < 50:
                    await message.channel.send("Tú mensaje debe superar los 50 carácteres.")

                else:
                    member = self.guild.get_member(message.author.id)
                    embed = Embed(title="Modmail",
                                     colour=member.colour,
                                     time_stamp=datetime.utcnow())

                    embed.set_thumbnail(url=member.avatar_url)

                    fields = [("Miembro", member.display_name, False),
                              ("Message", message.content, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                                                                               #mod = self.get_cog("Mod")  
                    await self.stdout.send(embed=embed)
                    await message.channel.send("Mensaje enviado a los moderadores.")

            await self.process_commands(message)

bot = Bot()
