import os
from dotenv import load_dotenv
import simplematrixbotlib as botlib
import requests
import shlex
from datetime import datetime, timezone, timedelta


load_dotenv()
homeserver = os.environ.get("HOMESERVER_URL")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

config = botlib.Config()
config.encryption_enabled = True
config.emoji_verify = True
config.ignore_unverified_devices = False
config.store_path = './crypto_store/'

creds = botlib.Creds(homeserver, username, password)
bot = botlib.Bot(creds)
PREFIX = '!'
servers = []


@bot.listener.on_message_event
async def echo(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)

    if match.is_not_from_this_bot() and match.prefix() and match.command("servers"):
        r = requests.get('https://hub.spacestation14.com/api/servers')
        servers=[]
        servers_data={}
        data = r.json()
        for x in data:
            servers.append(x["statusData"]["name"])
        await bot.api.send_markdown_message(
            room.room_id, "```\n"+"\n".join(servers)+"\n```"
            )
    elif match.is_not_from_this_bot() and match.prefix() and match.command("help"):
        await bot.api.send_markdown_message(
            room.room_id, "!help for this"+"\n !servers to print all servers"+"\n !status to fetch status of a server"
            )
    elif match.is_not_from_this_bot() and match.prefix() and match.command("status"):
        body = message.body
        body2 = shlex.split(body)
        agrs = body2[1]
        r = requests.get('https://hub.spacestation14.com/api/servers')
        servers=[]
        servers_data={}
        data = r.json()
        for x in data:
            statusData = x.get("statusData", {})
            servers.append(x["statusData"]["name"])
            servers_data[x["statusData"]["name"]] = {
                "map": statusData.get("map"),
                "preset": statusData.get("preset"),
                "players": statusData.get("players"),
                "round_id": statusData.get("round_id"),
                "round_start_time": statusData.get("round_start_time"),
                "queue": statusData.get("queue"),
                "max_players": statusData.get("soft_max_players")
                }

        index = next((i for i, s in enumerate(servers) if agrs.lower() in s.lower()), None)
        if index is not None:
            name = (servers[index])
            output= ""
#            print(name)
            output =(name)
            map1 =""
            server_data = servers_data[servers[index]]
#            print(server_data)
#            print(f"**Players:** {server_data['players']}/{server_data['max_players']}")
            output=(output+"\n"+f"**Players:** {server_data['players']}/{server_data['max_players']}")
#            print(f"**Map:** {server_data['map']}")
            output=(output+"\n"+f"**Map:** {server_data['map']}")
#            print(f"**Preset:** {server_data['preset']}")
            output=(output+"\n"+f"**Preset:** {server_data['preset']}")
#            print(f"######- Round ID: {server_data['round_id']}")
            output=(output+"\n"+f"###### Round ID: {server_data['round_id']}")
#            print("output"+output)
            await bot.api.send_markdown_message(
            room.room_id, " "+output
            )
        else:
            await bot.api.send_text_message(
            room.room_id, "Server not found "+agrs
            )
        
        
bot.run()