import discord
from discord.ext import commands
import os
import json
from google import genai  # The new 2026 library
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
# Initialize the new Google AI Client
ai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
TOKEN = os.getenv('DISCORD_TOKEN')

WELCOME_CHANNEL_ID = 1478417715743162450  
AUTO_ROLE_ID = 1445500038867583157      
THE_WARDEN_ID = 1331287355784560728 # <--- CHANGE THIS to your Discord ID!

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

last_thought = "Just standard bot stuff... or is it?"

# --- DATA HELPERS ---
def load_data():
    if not os.path.exists('data.json'):
        return {"updates": "No news yet.", "xp": {}}
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except:
        return {"updates": "No news yet.", "xp": {}}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f'✅ DUBIOUSASSISTENT is online and guarding RuneTap.')

@bot.event
async def on_member_join(member):
    # Give Role
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Role Error: {e}")

    # Welcome Message
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="✨ New Recruit Spotted!", 
            description=f"Welcome to Dubious Studios, {member.mention}!", 
            color=discord.Color.gold()
        )
        embed.add_field(name="Current Project", value="RuneTap", inline=False)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    global last_thought
    if message.author == bot.user:
        return

    # 1. XP System (Gives 5 XP per message)
    data = load_data()
    user_id = str(message.author.id)
    data["xp"][user_id] = data["xp"].get(user_id, 0) + 5
    save_data(data)

# 2. AI Logic (Only if @mentioned)
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            prompt = (
                f"User: '{message.content}'\n"
                "Format exactly like this: THOUGHT: [1-sentence dubious internal thought] | RESPONSE: [Direct response as DUBIOUSASSISTENT]"
            )
            
            response = ai_client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            
            full_res = response.text
            
            if "|" in full_res:
                parts = full_res.split("|")
                last_thought = parts[0].replace("THOUGHT:", "").strip()
                final_reply = parts[1].replace("RESPONSE:", "").strip()
                await message.channel.send(final_reply)
            else:
                await message.channel.send(full_res)

    # 3. Process Commands (Crucial for !rank and !when to work!)
    await bot.process_commands(message)

# --- COMMANDS ---
@bot.command()
async def thoughts(ctx):
    """See the bot's most recent secret thought."""
    await ctx.send(f"💭 **Internal Monologue:**\n> {last_thought}")

@bot.command()
async def when(ctx):
    """Check for RuneTap updates."""
    data = load_data()
    await ctx.send(f"📅 **RuneTap Intel:** {data['updates']}")

@bot.command()
async def set_update(ctx, *, info):
    """Change the update text (Warden only)."""
    if ctx.author.id == THE_WARDEN_ID:
        data = load_data()
        data["updates"] = info
        save_data(data)
        await ctx.send(f"✅ **Warden Log Updated:** {info}")
    else:
        await ctx.send("❌ Access Denied. Only The Warden can log updates.")

@bot.command()
async def rank(ctx, member: discord.Member = None):
    """Check your Level and XP."""
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
    else:
        await ctx.send(f"❌ {target.name} hasn't earned any XP yet!")

bot.run(TOKEN)
bot.run(TOKEN)
