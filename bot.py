# 導入 Discord.py
import imp
import urllib.request
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import discord
from discord.ext import commands
import asyncio
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
# client 是我們與 Discord 連結的橋樑
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
service = Service('./chromedriver')
options = Options()
options.add_argument("--disable-notifications")


def generate_mp3(s, translate=0):
    j_s = c2j(s) if translate else s

    driver = webdriver.Chrome(service=service, chrome_options=options)
    driver.get("https://huggingface.co/spaces/innnky/vits-nyaru")
    wait = WebDriverWait(driver, 10, poll_frequency=5)

    wait.until(lambda driver: driver.find_elements(
        By.TAG_NAME, 'iframe'))
    frames = driver.find_elements(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(frames[0])

    wait.until(lambda driver: driver.find_elements(
        By.TAG_NAME, 'textarea'))
    textarea = driver.find_elements(By.TAG_NAME, 'textarea')
    textarea[0].clear()
    textarea[0].send_keys(j_s)
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    buttons[2].click()

    wait.until(lambda driver: driver.find_elements(
        By.TAG_NAME, 'audio'))
    audio = driver.find_element(By.TAG_NAME, 'audio')
    audio_src = audio.get_attribute('src')
    urllib.request.urlretrieve(audio_src, f'{s}.mp3')
    driver.close()


def c2j(s):
    driver = webdriver.Chrome(service=service, chrome_options=options)
    driver.get(
        "https://www.chineseconverter.com/zh-tw/convert/chinese-characters-to-katakana-conversion")
    wait = WebDriverWait(driver, 10, poll_frequency=5)

    wait.until(lambda driver: driver.find_elements(
        By.TAG_NAME, 'textarea'))
    textarea = driver.find_element(By.TAG_NAME, 'textarea')
    button = driver.find_element(By.XPATH, '//*[@id="w0"]/div[3]/div/button')
    textarea.clear()
    textarea.send_keys(s)
    button.click()
    wait.until(lambda driver: driver.find_element(
        By.CLASS_NAME, 'result-html'))
    output_div = driver.find_element(By.CLASS_NAME, 'result-html')
    ouput_string = output_div.text.replace(" ", "")
    driver.close()
    return ouput_string


@bot.command()
async def playAudio(ctx, s):
    message_channel = discord.utils.get(
        ctx.message.guild.text_channels, name="呱")
    user = ctx.author
    voice_channel = user.voice.channel
    # only play music if user is in a voice channel
    if voice_channel != None:
        # grab user's voice channel
        # create StreamPlayer
        # This allows for more functionality with voice channels
        voice = discord.utils.get(
            bot.voice_clients, guild=voice_channel.guild)

        if voice == None:
            vc = await voice_channel.connect()
        else:
            await message_channel.send("I'm already connected!")
        vc.play(discord.FFmpegPCMAudio(f'{s}.mp3'),
                after=lambda e: print('done', e))
        while vc.is_playing():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        vc.stop()
        await vc.disconnect()
    else:
        await message_channel.send('User is not in a channel.')

# 調用 event 函式庫


@bot.event
# 當機器人完成啟動時
async def on_ready():
    print('目前登入身份：', bot.user)


@bot.command()
# 如果指令為jtts，機器人回傳或播放 audio
async def jtts(ctx, s, actions='-v'):
    # 排除 -
    action_list = list(actions)
    if action_list[0] != '-':
        return
    action_list = action_list[1:]

    message_channel = discord.utils.get(
        ctx.message.guild.text_channels, name="呱")

    # 如果包含 /jtts，機器人回傳或播放 audio
    fileName = f'{s}.mp3'

    isExist = os.path.isfile(fileName)
    translate = 'c' in action_list

    if (not isExist) or ('r' in action_list):
        generate_mp3(s, translate)

    if 'f' in action_list:
        await ctx.channel.send(file=discord.File(fileName))
    elif 'v' in action_list:
        await playAudio(ctx, s)


@bot.command()
# 如果指令為jtts，機器人回傳或播放 audio
async def helpme(ctx):
    help_content = '''
    /jtts {message} (-[r, f, v])

    message <the audio what you want to generate>

    -r <regenerate audio>

    -f <send audio file>

    -v <join voice channel and play audio>

    -c <generate by chinese>
    '''
    await ctx.send(help_content)

# TOKEN 在剛剛 Discord Developer 那邊「BOT」頁面裡面
bot.run(
    'MTAxMzc0OTM3MDI3OTE3ODI2MQ.G7P1e1.NCJU73jWulw66I9thAt13DAsm60NxZJsaw2g34')
