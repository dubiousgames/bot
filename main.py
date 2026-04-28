import discord
from discord.ext import commands
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash')
TOKEN = os.getenv('DISCORD_TOKEN')

WELCOME_CHANNEL_ID = 1478417715743162450  
AUTO_ROLE_ID = 1445500038867583157      
THE_WARDEN_ID = 123456789012345678 # <--- Put YOUR Discord ID here!

# Set up the bot with a prefix
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Needed for on_member_join!
bot = commands.Bot(command_prefix="!", intents=intents)

last_thought = "Just standard bot stuff... or is it?"

# --- DATA HELPERS ---
def load_data():
    if not os.path.exists('data.json'):
        return {"updates": "No news yet.", "xp": {}}
    with open('data.json', 'r') as f:
        return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f'DUBIOUSASSISTENT is online and guarding RuneTap.')

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except:
            pass # Usually fails if bot role is lower than target role

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="✨ New Recruit Spotted!", description=f"Welcome to Dubious Studios, {member.mention}!", color=discord.Color.gold())
        embed.add_field(name="Current Project", value="RuneTap", inline=False)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    global last_thought
    if message.author == bot.user:
        return

    # XP System: Give 5 XP per message
    data = load_data()
    user_id = str(message.author.id)
    data["xp"][user_id] = data["xp"].get(user_id, 0) + 5
    save_data(data)

    # Trigger AI only on @mentions
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            prompt = (f"User: '{message.content}'\nFormat: THOUGHT: [1-sentence dubious thought] | RESPONSE: [Actual response as DUBIOUSASSISTENT]")
            full_res = model.generate_content(prompt).text
            if "|" in full_res:
                parts = full_res.split("|")
                last_thought = parts[0].replace("THOUGHT:", "").strip()
                await message.channel.send(parts[1].replace("RESPONSE:", "").strip())
            else:
                await message.channel.send(full_res)

    # This line allows commands like !rank to still work!
    await bot.process_commands(message)

# --- COMMANDS ---
@bot.command()
async def thoughts(ctx):
    await ctx.send(f"💭 **Internal Monologue:**\n> {last_thought}")

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
    target = member or ctx.author
    data = load_data()
    user_id = str(target.id)
    if user_id in data["xp"]:
        xp = data["xp"][user_id]
        level = xp // 100
        embed = discord.Embed(title=f"📊 {target.name}'s Stats", color=discord.Color.green())
        embed.add_field(name="Level", value=f"**{level}**", inline=True)
        embed.add_field(name="Total XP", value=f"{xp}", inline=True)
        await ctx.send(embed=embed)

bot.run(TOKEN)
