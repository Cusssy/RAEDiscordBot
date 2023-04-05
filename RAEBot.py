import discord
import requests
import json
import os

if not os.path.isfile('errors.json'):
        f = open('errors.json', "w")
        f.write("""{"count": 0}""")
        f.close()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_errors():
    global errores
    with open('errors.json', 'r') as f:
        data = json.load(f)
        errores = data.get('count')

get_errors()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{errores} errores ortográficos'))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    url = 'https://languagetool.org/api/v2/check'
    data = {
        'text': message.content,
        'language': 'es-ES',
        'enabledOnly': 'false',
        'disabledRules': 'Rule.QuestionMarkRule'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=data, headers=headers)
    errors = json.loads(response.text)['matches']
    correct = ''
    try:
        correct = json.loads(response.text)['matches'][0]['replacements'][0]['value'] if len(json.loads(response.text)['matches']) > 0 else 'No hay errores ortográficos'
    except IndexError:
        pass
    if len(errors) > 0:
        try:
            await message.add_reaction('❌')
        except discord.errors.Forbidden:
            pass
        if correct == '':
            pass
        else:
            try:
                await message.channel.send(f"{correct}*")
            except discord.errors.Forbidden:
                pass
        get_errors()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{errores} errores ortográficos'))
        with open('errors.json', 'r') as f:
            errors_data = json.load(f)
            
        errors_data['count'] += len(errors)
        with open('errors.json', 'w') as f:
            json.dump(errors_data, f)

client.run('TOKEN')
