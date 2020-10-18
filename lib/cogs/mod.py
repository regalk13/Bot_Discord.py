from asyncio import sleep
from re import search

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Greedy
from better_profanity import profanity
from discord import Embed, Member
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions
from datetime import datetime, timedelta
from typing import Optional

from ..db import db

profanity.load_censor_words_from_file("./data/profanity.txt")

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.links_allowed = (760460794139377714,)
    
    async def kick_members(self, message, targets, reason):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
                await target.kick(reason=reason)

                embed = Embed(title="Miembro kickeado",
                              colour=0xDD2222,
                              time_stamp=datetime.utcnow())
                
                embed.set_thumbnail(url=target.avatar_url)
                
                fields = [("Miembro", f"{target.name} {target.display_name}", False),
                          ("Kickeado por", target.display_name, message.author.display_name, False),
                          ("Razón", reason, False)]
                
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                
                await self.log_channel.send(embed=embed)

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "Ninguna razón."):
        if not len(targets):
            await ctx.send("algún o algunos argumentos faltan.")

        else:
            await self.kick_members(ctx.message, targets, reason)
            await ctx.send("Acción completada.")

    @kick_command.error
    async def kick_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insuficientes permisos para kickear.")

    async def ban_members(self, message, targets, reason):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
                await target.ban(reason=reason)

                embed = Embed(title="Miembro baneado",
                              colour=0xDD2222,
                              time_stamp=datetime.utcnow())
                
                embed.set_thumbnail(url=target.avatar_url)
                
                fields = [("Miembro", f"{target.name}-{target.display_name}", False),
                          ("baneado por", message.author.display_name, False),
                          ("Razón", reason, False)]
                
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
 
                await self.log_channel.send(embed=embed)
    
    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "Ninguna razón."):
        if not len(targets):
            await ctx.send("algún o algunos argumentos faltan.")

        else:
            await self.ban_members(ctx.message, targets, reason)
            await ctx.send("Acción completada.")

    @ban_command.error
    async def ban_command_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insuficientes permisos para banear.")

    @command(name="clear", aliases=["purgue"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_menssages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
        def _check(message):
            return not len(targets) or message.author in targets
            
        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14),
                                                  check=_check) 

                await ctx.send(f"✅ Se han borrado {len(deleted):,} mensajes", delete_after=5)

        else:
            await ctx.send("El número de mensajes que desea borrar no esta entre los limites.")

    async def unmute(self, ctx, targets, reason="Tiempo de mute expirado."):
        for target in targets:
            if self.mute_role in target.roles:
                role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", target.id)
                roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

                await target.remove_roles(target.guild.get_role(764653159452114954))

                await ctx.send(f"{target.mention} ha sido desmuteado.")
            
    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def unmute_members(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "Ninguna razón"):
        if not len(targets):
            await ctx.send("Por favor indica al miembro muteado.")

        else:
            for target in targets:
                await self.unmute(ctx, targets, reason=reason)
                await target.send(f"Has sido desmuteado por {reason}.")

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)
    async def mute_members(self, message, targets: Greedy[Member], hours: Optional[int], *, reason: Optional[str] = "Ninguna razón"):
        if not len(targets):
            await message.channel.send("Por favor indica el miembro a mutear.")

        else:
            unmutes = []

            for target in targets:
                if not self.mute_role in target.roles:
                    if message.guild.me.top_role.position > target.top_role.position:
                        role_ids = ",".join([str(r.id) for r in target.roles])
                        end_time = datetime.utcnow() + timedelta(seconds=hours*3600) if hours else None

                        db.execute("INSERT INTO mutes VALUES (?, ?, ?)", target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

                        await target.add_roles(target.guild.get_role(764653159452114954))
                        await message.channel.send(f"{target.mention} ha sido muteado durante {hours} hora(s)")
                        await target.send(f"Has sido muteado del server por {reason}.")
                        
                        if hours:
                            unmutes.append(target)

                    else:
                        await message.channel.send(f"{target.mention} no puede ser muteado.")

                else:
                    await message.channel.send(f"{target.display_name} ya está muteado.")

            if len(unmutes):
                await sleep(hours)
                await self.unmute(message, targets)

    @command(name="addprofanity", aliases=["addswears", "addcurses"])
    @has_permissions(manage_guild=True)
    async def add_profanity(self, ctx, *words):
	    with open("./data/profanity.txt", "a", encoding="utf-8") as f:
		    f.write("".join([f"{w}\n" for w in words]))

	    profanity.load_censor_words_from_file("./data/profanity.txt")
	    await ctx.send("Acción completada.")

    @command(name="delprofanity", aliases=["delswears", "delcurses"])
    @has_permissions(manage_guild=True)
    async def remove_profanity(self, ctx, *words):
        with open("./data/profanity.txt", "r", encoding="utf-8") as f:
            stored = [w.strip() for w in f.readlines()]

        with open("./data/profanity.txt", "w", encoding="utf-8") as f:
            f.write("".join([f"{w}\n" for w in stored if w not in words]))

        profanity.load_censor_words_from_file("./data/profanity.txt")
        await ctx.send("Acción completada.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
               self.log_channel = self.bot.get_channel(762403035586101288)
               self.mute_role = self.bot.guild.get_role(764557420788842538)
               self.bot.cogs_ready.ready_up("mod")

    @Cog.listener()
    async def on_message(self, message):
        def _check(m):
            return (m.author == message.author
                    and len(m.mentions)
                    and (datetime.utcnow()-m.created_at).seconds < 60)

        if not message.author.bot:
            if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= 5:
                await message.channel.send("No hagas SPAM de menciones!", delete_after=10)
                unmutes = await self.mute_members(message, [message.author], 5, reason="SPAM de menciones")

                if len(unmutes):
                    await sleep(5)
                    await self.unmute_members(message.guild, [message.author])

            if profanity.contains_profanity(message.content):
                await message.delete()
                await message.channel.send("Mejora tú vocabulario por favor.", delete_after=10)

            elif message.channel.id not in self.links_allowed and search(self.url_regex, message.content):
                await message.delete()
                await message.channel.send("No puedes enviar links aquí.", delete_after=10)

def setup(bot):
    bot.add_cog(Mod(bot))

