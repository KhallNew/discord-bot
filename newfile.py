import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta, timezone

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

# ---------- DATA HANDLING ----------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def check_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {}
    user = users[str(user_id)]
    user.setdefault("money", 0)
    user.setdefault("bank", 0)
    user.setdefault("items", [])
    user.setdefault("last_daily", None)
    user.setdefault("last_weekly", None)

def progress_bar(value, max_value=1000, length=20):
    # Visual bar proportional dengan max_value
    filled = int((value / max_value) * length)
    filled = min(filled, length)
    empty = length - filled
    return "🟩"*filled + "⬜"*empty

def get_total(user_data):
    return user_data.get("money",0) + user_data.get("bank",0)

# ---------- MENU SUPER VISUAL ----------
@bot.command(name="menu")
async def menu(ctx):
    embed = discord.Embed(
        title="📜 Menu Bot Ekonomi Super Visual",
        description="Berikut command yang bisa kamu gunakan:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="💰 Ekonomi", value=(
        "`!saldo` - Dashboard uang & bank\n"
        "`!kerja` - Kerja harian dapat uang\n"
        "`!simpan <jumlah>` - Simpan ke bank\n"
        "`!tarik <jumlah>` - Tarik dari bank"
    ), inline=False)
    embed.add_field(name="🛒 Shop & Inventory", value=(
        "`!shop` - Lihat item tersedia\n"
        "`!beli <item>` - Beli item\n"
        "`!jual <item>` - Jual item\n"
        "`!inventory` - Lihat item yang dimiliki"
    ), inline=False)
    embed.add_field(name="🎁 Reward", value=(
        "`!daily` - Klaim daily reward\n"
        "`!weekly` - Klaim weekly reward"
    ), inline=False)
    embed.add_field(name="🏆 Leaderboard", value="`!leaderboard` - Ranking top 10 player", inline=False)
    embed.set_footer(text="Nikmati bot ekonomi super visual!")
    await ctx.send(embed=embed)

# ---------- DASHBOARD SUPER VISUAL ----------
@bot.command()
async def saldo(ctx):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    max_value = max(data["money"], data["bank"], 1000)  # max untuk visual
    embed = discord.Embed(
        title=f"{ctx.author.name}'s Dashboard 💼",
        description="💹 Status ekonomi kamu saat ini",
        color=discord.Color.green()
    )
    embed.add_field(name="Cash 💰", value=f"{progress_bar(data['money'], max_value)}\n**{data['money']}**", inline=False)
    embed.add_field(name="Bank 🏦", value=f"{progress_bar(data['bank'], max_value)}\n**{data['bank']}**", inline=False)
    embed.add_field(name="Inventory 🛍️", value=", ".join(data["items"]) or "Kosong", inline=False)
    embed.set_footer(text="Gunakan !kerja, !shop, !daily untuk mendapatkan reward")
    await ctx.send(embed=embed)

# ---------- WORK SUPER VISUAL ----------
@bot.command()
async def kerja(ctx):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    hasil = random.randint(50, 200)
    data["money"] += hasil
    save_users()
    embed = discord.Embed(
        title="Kerja Harian 🛠️",
        description=f"{ctx.author.mention} bekerja dan mendapatkan 💵 **{hasil}**!",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("💰")

# ---------- BANK SUPER VISUAL ----------
@bot.command()
async def simpan(ctx, jumlah: int):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    if jumlah <= 0:
        return await ctx.send(f"{ctx.author.mention}, jumlah harus lebih dari 0!")
    if data["money"] >= jumlah:
        data["money"] -= jumlah
        data["bank"] += jumlah
        save_users()
        embed = discord.Embed(
            title="Bank 🏦",
            description=f"{ctx.author.mention} menyimpan 💵 **{jumlah}** ke bank!",
            color=discord.Color.purple()
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
    else:
        await ctx.send(f"{ctx.author.mention}, saldo kamu tidak cukup!")

@bot.command()
async def tarik(ctx, jumlah: int):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    if jumlah <= 0:
        return await ctx.send(f"{ctx.author.mention}, jumlah harus lebih dari 0!")
    if data["bank"] >= jumlah:
        data["bank"] -= jumlah
        data["money"] += jumlah
        save_users()
        embed = discord.Embed(
            title="Bank 🏦",
            description=f"{ctx.author.mention} menarik 💵 **{jumlah}** dari bank!",
            color=discord.Color.gold()
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("💸")
    else:
        await ctx.send(f"{ctx.author.mention}, saldo bank kamu tidak cukup!")

# ---------- SHOP & INVENTORY SUPER VISUAL ----------
shop_items = {
    "Potion": 100,
    "Sword": 500,
    "Shield": 300,
    "Magic Scroll": 1000
}

@bot.command()
async def shop(ctx):
    embed = discord.Embed(
        title="🛒 Shop Super Visual",
        description="Beli item untuk meningkatkan pengalamanmu!",
        color=discord.Color.orange()
    )
    for item, price in shop_items.items():
        embed.add_field(name=f"{item} 🏷️", value=f"💰 {price}", inline=True)
    embed.set_footer(text="Beli: !beli <item> | Jual: !jual <item>")
    await ctx.send(embed=embed)

@bot.command()
async def inventory(ctx):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    embed = discord.Embed(
        title=f"{ctx.author.name}'s Inventory 🛍️",
        description="Daftar item yang kamu miliki:",
        color=discord.Color.teal()
    )
    embed.add_field(name="Items", value=", ".join(data["items"]) or "Kosong", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def beli(ctx, *, item):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    item = item.title()
    if item not in shop_items:
        return await ctx.send(f"{ctx.author.mention}, item tidak tersedia!")
    price = shop_items[item]
    if data["money"] >= price:
        data["money"] -= price
        data["items"].append(item)
        save_users()
        embed = discord.Embed(
            title="🛍️ Pembelian Berhasil",
            description=f"{ctx.author.mention} membeli **{item}** seharga 💰 {price}!",
            color=discord.Color.green()
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✨")
    else:
        await ctx.send(f"{ctx.author.mention}, saldo kamu tidak cukup!")

@bot.command()
async def jual(ctx, *, item):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    item = item.title()
    if item not in data["items"]:
        return await ctx.send(f"{ctx.author.mention}, kamu tidak memiliki {item}!")
    sell_price = shop_items.get(item,100)//2
    data["money"] += sell_price
    data["items"].remove(item)
    save_users()
    embed = discord.Embed(
        title="💰 Penjualan Berhasil",
        description=f"{ctx.author.mention} menjual **{item}** dan mendapatkan 💵 {sell_price}",
        color=discord.Color.gold()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("💸")

# ---------- DAILY & WEEKLY SUPER VISUAL ----------
@bot.command()
async def daily(ctx):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    now = datetime.utcnow()
    last = data.get("last_daily")
    if last:
        last = datetime.fromisoformat(last)
        if now - last < timedelta(hours=24):
            return await ctx.send(f"{ctx.author.mention}, kamu sudah klaim daily hari ini!")
    reward = random.randint(100, 300)
    data["money"] += reward
    data["last_daily"] = now.isoformat()
    save_users()
    embed = discord.Embed(
        title="🎁 Daily Reward",
        description=f"{ctx.author.mention} mendapatkan 💰 **{reward}** dari daily reward!",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

@bot.command()
async def weekly(ctx):
    check_user(ctx.author.id)
    data = users[str(ctx.author.id)]
    now = datetime.utcnow()
    last = data.get("last_weekly")
    if last:
        last = datetime.fromisoformat(last)
        if now - last < timedelta(days=7):
            return await ctx.send(f"{ctx.author.mention}, kamu sudah klaim weekly reward minggu ini!")
    reward = random.randint(500, 1000)
    data["money"] += reward
    data["last_weekly"] = now.isoformat()
    save_users()
    embed = discord.Embed(
        title="🎁 Weekly Reward",
        description=f"{ctx.author.mention} mendapatkan 💰 **{reward}** dari weekly reward!",
        color=discord.Color.gold()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🏅")

# ---------- LEADERBOARD SUPER VISUAL ----------
@bot.command()
async def leaderboard(ctx):
    leaderboard = sorted(users.items(), key=lambda x: get_total(x[1]), reverse=True)
    embed = discord.Embed(
        title="🏆 Leaderboard Ekonomi Super Visual",
        color=discord.Color.gold()
    )
    for i,(user_id,data) in enumerate(leaderboard[:10],start=1):
        member = ctx.guild.get_member(int(user_id))
        if member:
            total = get_total(data)
            medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else ""
            embed.add_field(name=f"{i}. {member.name} {medal}", value=f"💰 Total: {total}", inline=False)
    await ctx.send(embed=embed)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN belum diset di Railway Variables")

bot.run(TOKEN)