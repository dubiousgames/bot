import discord
import random
import json
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv() # This looks for a .env file locally
TOKEN = os.getenv('DISCORD_TOKEN') # This looks for the GitHub Secret if the file is missing

# --- INTENTS
intents = discord.Intents.all() # This tells Discord "I want access to EVERYTHING"
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)  

# 3. Setup the Bot & Warden
THE_WARDEN_ID = 1331287355784560728
bot = commands.Bot(command_prefix='!', intents=intents)

# --- THE BRAIN (Data Loading) ---
def save_data(data):
    with open('studio_data.json', 'w') as f:
        json.dump(data, f)

def load_data():
    try:
        with open('studio_data.json', 'r') as f:
            return json.load(f)
    except:
        return {"xp": {}, "updates": "No update date set yet."}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has arrived at Dubious Studios!')
    print(f'🛡️ Security active for Warden ID: {THE_WARDEN_ID}')

@bot.event
async def on_message(message):
    # This will print in your black terminal window every time a message is sent
    print(f"📩 [{message.author}] said: {message.content}")

    if message.author.bot:
        return

    # Check if the bot thinks the person talking is the Warden
    if message.author.id == THE_WARDEN_ID:
        print(f"👑 Warden {message.author} is speaking. Ignoring security checks.")
        # We still want the Warden to be able to use commands
        await bot.process_commands(message)
        return

    content = message.content.lower()

    # --- HAMURGER TEST ---
    if 'hamurger' in content:
        print("🍔 Hamurger detected!")
        await message.channel.send("🍔 Secret word detected!")

    # --- BAN TEST ---
    if os.path.exists('ban_words.txt'):
        with open('ban_words.txt', 'r') as f:
            ban_list = [line.strip().lower() for line in f if line.strip()]
        
        for slur in ban_list:
            if slur in content:
                print(f"🔨 Attempting to ban {message.author} for '{slur}'")
                await message.delete()
                await message.author.ban(reason=f"Auto-Mod: {slur}")
                return

    await bot.process_commands(message)

# --- WELCOME PROTOCOL ---
WELCOME_CHANNEL_ID = 1478417715743162450  # <--- Replace with your Channel ID
AUTO_ROLE_ID = 1445500038867583157      # <--- Replace with your Role ID

@bot.event
async def on_member_join(member):
    # 1. Give the role automatically
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
            print(f"✅ Assigned role to {member.name}")
        except Exception as e:
            print(f"❌ Could not give role: {e}")

    # 2. Send the welcome message
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        welcome_embed = discord.Embed(
            title="✨ New Recruit Spotted!",
            description=f"Welcome to Dubious Studios, {member.mention}!",
            color=discord.Color.gold()
        )
        welcome_embed.add_field(name="Current Project", value="RuneTap", inline=False)
        welcome_embed.set_footer(text="Check out the rules and have fun!")
        
        await channel.send(embed=welcome_embed)

# --- COMMANDS ---
@bot.command()
async def when(ctx):
    data = load_data()
    await ctx.send(f"📅 **RuneTap Intel:** {data['updates']}")

@bot.command()
async def set_update(ctx, *, info):
    if ctx.author.id == THE_WARDEN_ID:
        data = load_data()
        data["updates"] = info
        save_data(data)
        await ctx.send(f"✅ **Warden Log Updated:** {info}")

@bot.command()
async def rank(ctx, member: discord.Member = None):
    # If you don't mention anyone, it shows your own rank
    target = member or ctx.author
    
    data = load_data()
    user_id = str(target.id)
    
    if user_id in data["xp"]:
        xp = data["xp"][user_id]
        level = xp // 100
        xp_needed = 100 - (xp % 100)
        
        embed = discord.Embed(
            title=f"📊 {target.name}'s Stats",
            color=discord.Color.green()
        )
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Total XP", value=f"{xp}", inline=True)
        embed.add_field(name="Next Level In", value=f"{xp_needed} XP", inline=False)
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {target.name} hasn't earned any XP yet. Start chatting!")


#   TOKEN THING

bot.run(TOKEN)
