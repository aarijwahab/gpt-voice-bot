import os
import openai
from dotenv import load_dotenv
import fakeyou
from datetime import datetime
import discord
from discord import FFmpegPCMAudio

#HOW TO SEARCH FOR MODEL TOKENS.
# result=fy.search("Ichigo")
# for title, model in zip(result.voices.title, result.voices.modelTokens):
# 	print(title, model)

def logmsg(type,message):
  print(f'{datetime.now()}/{type}:{message}')


def generatePrompt(character):
  prompt=f"""
  Create a sentence from the following information: 
  The sentence should include some reference to: {character["mustReference"]}. 
  It should be written in the style of: A hip hop rap. 
  Limit is 200 characters.
  """
  return prompt


async def createSentence(character):
  prompt = generatePrompt(character)
  response = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  temperature=0.7,
  max_tokens=64,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
  )
  sentence = response['choices'][0]['text']
  logmsg("INFO","Generating voice file")
  fy.say(text=sentence,ttsModelToken=character["modelToken"])



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

  voicesDict = {
    "Ichigo": {"modelToken":"TM:akvty90pyxx3", "mustReference":"Soul Society"},
    "Goku": {"modelToken": "TM:8yb40ydx7t1p", "mustReference":"Saving the universe"}
  }

  try:
    logmsg("INFO","Logging into fakeyou.com")
    fy.login(fy_user,fy_pass)
  except fakeyou.exception.InvalidCredentials:
    logmsg("INFO","Failed to Log in")

  @client.event
  async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    print(msg)

    if msg.startswith('!voice') and message.author.voice:
      print('Message started with voice')
      msg_words = msg.split()
      logmsg("INFO","Creating sentence from prompt")
      await createSentence(voicesDict[msg_words[1]])
      channel = message.author.voice.channel
      voice = await channel.connect()
      source = FFmpegPCMAudio('fakeyou.wav')
      player = await voice.play(source)
      logmsg("INFO","Task completed successfully")
      await message.guild.voice_client.disconnect()

  client.run(discord_token)
