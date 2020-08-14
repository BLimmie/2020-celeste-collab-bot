async def try_send(member, message):
    try:
        await member.send(message)
    except:
        print("Unable to send PM")

def find_member(guild,id):
    return guild.get_member(int(id)).display_name