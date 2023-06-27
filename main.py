#setup and imports
import discord
from discord.ext import commands
from discord.utils import get
from keep_alive import keep_alive

import os
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


#DOTENV variables
disc_token = os.environ.get("disctoken")
s_ID = os.environ.get("spreadsheetID")

#Spreadsheet Setup
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

#Gets all the data from the spreadsheet and produces a nested list separated by column in the spreadsheet
results = sheet.values().get(spreadsheetId=s_ID, range="Sheet1!B2:E8", majorDimension="COLUMNS").execute()
values = results.get('values', [])

#Following lines separates the data in the list and stores them to their appropriate variables
emails = []
for item in values[0]:
  emails.append(item.lower())

committees = []
for item in values[1]:
  committees.append(item)

country = []
for item in values[2]:
  country.append(item)

ConfRole = []
for item in values[3]:
  ConfRole.append(item)

#Functions
def get_info(email, emails=emails , committees=committees, country=country, ConfRole=ConfRole):
  '''
  Parameters: email of delegate, and the global variables of emails, committees, country and ConfRole

  Returns: a list with the committee, country and role of the delegate
  '''
  try:
    index = emails.index(email)

    return [committees[index], country[index], ConfRole[index]]
    '''
    returns 0: committee
            1: country
            2: position
    '''

  except:
    return None



#Discord Bot Starts Here
intents = discord.Intents().all()
client = commands.Bot(command_prefix="-", intents=intents)

#standard output when the bot turns on
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="our participants!"))
  print("We have logged in as {0.user}".format(client))

#adds unverified role upon joining the server
@client.event
async def on_member_join(member):
    role = get(member.guild.roles, name="unverified")
    await member.add_roles(role)

#clear command to easily get rid of messages in chats
@client.command(aliases=["C", "c", "Clear"])
async def clear(ctx, num):
  await ctx.channel.purge(limit = int(num))

#command for placards in chat
@client.command()
async def placards(ctx):
  if ctx.author.id == 495266674908463114:
    await ctx.channel.purge(limit = 1)
    await ctx.send("Placards // Please press on the flag reaction of your delegation when you want to raise a hand!")

#command for voting in chat
@client.command()
async def voting(ctx):
  if ctx.author.id == 495266674908463114:
    await ctx.channel.purge(limit = 1)
    await ctx.send("Voting // Please press on green to vote 'for', red to vote 'against' and white to 'abstain'!")

'''
BEAUTIFUL COMMAND RIGHT HERE
The command allows users to automatically verify themselves by inputting their email, they will be given all their appropriate roles and will be renamed accordingly.
'''
@client.command()
async def verify(ctx, email):
    member = ctx.author
    channel = ctx.message.channel.id

    if channel == 775707080510013501:
      email = email.lower()
      del_info = get_info(email)

      if del_info == None:
        await ctx.send("Make sure you have typed in your email correctly and it's the one you have used to sign up for this conference!")

      else:
        
        for item in del_info[::2]:
          #adds roles
          role = get(member.guild.roles, name=item)
          await member.add_roles(role)

        #removes unverified role
        role = get(member.guild.roles, name="unverified")
        await member.remove_roles(role)

        #changed the server nickname for the participant according to their position
        nickname = "["+del_info[0]+"] "+del_info[1]
        await member.edit(nick=nickname)

        await ctx.send(f"Successfully given roles to {member.mention}!")

    else:
      await ctx.send("Please only use this command in #verify!")



keep_alive() #function for website
client.run(disc_token)
