import os
import openai
from dotenv import load_dotenv
import fakeyou
from datetime import datetime
import discord
from discord import FFmpegPCMAudio
from termcolor import colored
import random

def logmsg(type,message,color="green"):
  print(colored(f"{datetime.now()}    {type}: {message}",color))


async def createSentence(character, style=""):
  if style == "":
    styles = ['Action', 'Mystery', 'RomCom', 'Thriller', 'SciFi', 'Drama', 'Western', 'Fantasy', 'History', 'Horror']
    style = styles[random.randint(0,len(styles)-1)]
  prompt=f"""
  Create a sentence from the following information: 
  The sentence should include some reference to the following: {character["mustReference"]}. 
  It should be written in the style of: {style}. 
  Limit is 200 characters.
  """
  response = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  temperature=0.7,
  max_tokens=64,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
  )
  sentence = response["choices"][0]["text"]
  try:
    logmsg("INFO","Generating voice file")
    fy.say(text=sentence,ttsModelToken=character["modelToken"])
  except Exception as e:
    logmsg("ERROR","Could not generate voice file","red")

async def sayPrompt(character, prompt):
  try:
    logmsg("INFO","Generating voice file")
    fy.say(text=prompt, ttsModelToken=character["modelToken"])
  except Exception as e:
    logmsg("ERROR","Could not generate voice file","red")
    logmsg("ERROR",str(e),"red")

# print()
if __name__ == "__main__":
  load_dotenv()

  openai.api_key = os.getenv("OPENAI_API_KEY")
  fy_user=os.getenv("FAKEYOU_USER")
  fy_pass=os.getenv("FAKEYOU_PASS")
  fy=fakeyou.FakeYou()
  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Client(intents=intents)
  discord_token = os.getenv("DISCORD_TOKEN")
  logmsg("INFO",discord_token)

  #HOW TO SEARCH FOR MODEL TOKENS.
  # result=fy.search("Trump")
  # for title, model in zip(result.voices.title, result.voices.modelTokens):
  # 	print(title, model)


  voicesDict = {
    "ichigo": {"modelToken":"TM:akvty90pyxx3", "mustReference":"Soul Society"},
    "goku": {"modelToken": "TM:8yb40ydx7t1p", "mustReference":"Saving the universe"},
    "mario": {"modelToken": "TM:c7j599fz0pbg", "mustReference":"The Mushroom Kingdom"},
    "naruto": {"modelToken": "TM:yn4n7kwj9404", "mustReference":"The Hidden Leaf Village"},
    "trump": {"modelToken": "TM:aejrk66wq3ss", "mustReference":"Hating Everyone"}
  }

  try:
    logmsg("INFO","Logging into fakeyou.com")
    fy.login(fy_user,fy_pass)
  except fakeyou.exception.InvalidCredentials:
    logmsg("ERROR","Failed to Log in","red")

  @client.event
  async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    print(msg)

    if msg.startswith("!voice") and message.author.voice:
      logmsg("INFO","Message started with voice")
      msg_words = msg.split()
      logmsg("INFO","Creating message from prompt")
      character = msg_words[1].lower()
      if len(msg_words) == 2:
        await createSentence(voicesDict[character])
      elif len(msg_words) > 2:
        style = " ".join(msg_words[2:len(msg_words)])
        print(style)
        await createSentence(voicesDict[character], style)
      source = FFmpegPCMAudio("fakeyou.wav")
      if (not message.guild.voice_client):
        channel = message.author.voice.channel
        logmsg("INFO","Connecting to voice channel")
        voice = await channel.connect()
        logmsg("INFO", "Playing voice")
        voice.play(source, after=voice.stop())
      else:
        voice = message.guild.voice_client
        voice.play(source)
    elif msg.startswith("!prompt") and message.author.voice:
      logmsg("INFO","Message started with voice")
      msg_words = msg.split()
      if len(msg_words) < 3:
        return
      character = msg_words[1]
      prompt = " ".join(msg_words[2:len(msg_words)])
      await sayPrompt(voicesDict[character], prompt)
      source = FFmpegPCMAudio("fakeyou.wav")
      if (not message.guild.voice_client):
        channel = message.author.voice.channel
        logmsg("INFO","Connecting to voice channel")
        voice = await channel.connect()
        logmsg("INFO", "Playing voice")
        voice.play(source, after=voice.stop())
      else:
        voice = message.guild.voice_client
        voice.play(source)

      logmsg("INFO","Task completed successfully")

client.run(discord_token)
