from datetime import time

from src.modules.db_helper import insert_time, fetch_member, fetch_times
from src.modules.discord_helper import try_send, find_member
from src.modules.map_finder import find_map, find_label
from src.tools.message_return import message_data


def init(bot):
    @bot.command_on_message()
    def help(message):
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "Collab Bot Commands",
                "description": "Everything in brackets are information to be filled in. Do not write the brackets in the final command.",
                "color": 53380,
                "fields": [
                    {
                        "name": "$help",
                        "value": "Help dialog",
                        "inline": False
                    },
                    {
                        "name": "$pb [map name];[mm:ss.xxx];[link to video] [anything else]",
                        "value": "Submit an IL run to the leaderboards. $rules to read more. Semicolons let the bot know the difference between fields because the creator of this bot was too lazy to write a regex for this.",
                        "inline": False
                    },
                    {
                        "name": "$rules",
                        "value": "Rules for submitting IL runs",
                        "inline": False
                    },
                    {
                        "name": "$leaderboard [map name]",
                        "value": "Get the leaderboard for a specific map",
                        "inline": False
                    },
                    {
                        "name": "$mytimes",
                        "value": "Get your IL PB times",
                        "inline": False
                    },
                    {
                        "name": "$bug [Label];[Summary];[Description]",
                        "value": "Submit a bug report. $bughelp for more details. Semicolons let the bot know the difference between fields because the creator of this bot was too lazy to write a regex for this.",
                        "inline": False
                    },
                    {
                        "name": "$bughelp",
                        "value": "Help for sumbitting a bug report",
                        "inline": False
                    },
                    {
                        "name": "$buglist",
                        "value": "Link to current list of known bugs",
                        "inline": False
                    }
                ]
            }
        )

    async def verification(message, conn, map_name, member, map_time, desc):
        if conn is None:
            return
        try:
            await member.send(
                f'Your run is being verified for {map_name}. If this is the wrong map, please submit another run.')
        except:
            print("Unable to send PM")
        await message.add_reaction('✅')
        await message.add_reaction('❌')

        def check(reaction, user):
            return reaction.message.id == message.id and not user.bot and (
                    str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

        reaction, user = await bot.client.wait_for("reaction_add", check=check)
        if str(reaction.emoji) == '✅':
            insert_time(conn, member.id, map_name, map_time, desc)
            await try_send(member, f"Your run for {map_name} has been verified")
        else:
            await try_send(member,
                           f"Your run for {map_name} has been rejected. Please message the verifiers for clarification.")

    @bot.command_on_message(coro=verification)
    def pb(message):
        user = message.author
        content = message.content
        split_content = content.split(';')
        if len(split_content) < 3:
            return message_data(
                message.channel,
                "Usage: $pb [map name];[mm:ss.xxx];[link to video] [anything else]",
                args=[None, None, None, None]
            )
        else:
            try:
                map_time = time.fromisoformat(split_content[1].strip()).isoformat()[:-3]
            except:
                return message_data(
                    message.channel,
                    "Invalid time format",
                    args=[None, None, None, None]
                )
            map_name, _ = find_map(bot.config["maps"], split_content[0][split_content[0].find(' ') + 1:].strip())
            return message_data(
                bot.config["verification_channel"],
                message="",
                embed={
                    "title": "Verification Required",
                    "description": f"{map_name}",
                    "color": 53380,
                    "fields": [
                        {
                            "name": "Time",
                            "value": f"{map_time}",
                            "inline": False
                        },
                        {
                            "name": "Additional Information",
                            "value": f"{split_content[2]}",
                            "inline": False
                        }
                    ]
                },
                args=[bot.conn, map_name, user, map_time, split_content[2]]
            )

    @bot.command_on_message()
    def rules(message):
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "Speedrunning IL Rules",
                "description": "$pb [map name];[mm:ss.xxx];[link to video] [anything else]",
                "color": 53380,
                "fields": [
                    {
                        "name": "Recording",
                        "value": "A recording is necessary to be verified",
                        "inline": False
                    },
                    {
                        "name": "Timing",
                        "value": "Timing is done using the speedberry timer. Make sure the recording does not cover "
                                 "the timer.",
                        "inline": False
                    }
                ]
            }
        )

    @bot.command_on_message()
    def leaderboard(message):
        """
        $leaderboard mapname
        """
        content = message.content
        map_name = find_map(bot.config["maps"], content[content.find(' ') + 1:].strip())
        times = fetch_times(bot.conn, map_name)
        times.sort(key=lambda t: t[2])
        fields = [
            {
                "name": f"{find_member(message.channel.guild, id)}",
                "value": f"{map_time}",
                "inline": False
            }
            for (id, _, map_time, desc) in times
        ]
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "IL Leaderboard",
                "description": f"{map_name}",
                "color": 53380,
                "fields": fields
            }
        )

    @bot.command_on_message()
    def mytimes(message):
        id = message.author.id
        times = fetch_member(bot.conn, id)
        if times is None:
            return
        fields = [
            {
                "name": f"{map_name}",
                "value": f"{map_time} {desc}",
                "inline": False
            }
            for (_, map_name, map_time, desc) in times
        ]
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "IL Leaderboard",
                "description": f"{find_member(message.channel.guild, id)}'s IL Times",
                "color": 53380,
                "fields": fields
            }
        )

    @bot.command_on_message()
    def bughelp(message):
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "Bug Reporting Help",
                "description": "$bug [Label];[Summary];[Description]",
                "color": 53380,
                "fields": [
                    {
                        "name": "Valid Labels",
                        "value": "Bug, Gameplay, Visual, Speedrun, Accessibility, Other",
                        "inline": False
                    },
                    {
                        "name": "Bug",
                        "value": "Bugs in the Spring Collab code mod",
                        "inline": False
                    },
                    {
                        "name": "Gameplay",
                        "value": "Fixes to gameplay",
                        "inline": False
                    },
                    {
                        "name": "Visual",
                        "value": "Visual bugs/inconsistencies",
                        "inline": False
                    },
                    {
                        "name": "Speedrun",
                        "value": "Nerfs/buffs to speed berries",
                        "inline": False
                    },
                    {
                        "name": "Accessibility",
                        "value": "Fixes to anything that make a map inaccessible to a certain group of people",
                        "inline": False
                    },
                    {
                        "name": "Summary",
                        "value": "A short summary of the bug found (please avoid semicolons)",
                        "inline": False
                    },
                    {
                        "name": "Description",
                        "value": "Describe in detail what bug you found, or a suggested fix. Images/Videos should be "
                                 "uploaded to a hosting service such as Imgur/Streamable and linked in the "
                                 "description.",
                        "inline": False
                    }
                ]
            }
        )

    @bot.command_on_message()
    def bug(message):
        content = message.content
        submitter = message.author.display_name
        info = content[content.find(' ') + 1:].strip()
        split_content = info.split(';')
        if len(split_content) != 3:
            return message_data(
                message.channel,
                "Usage: $bug [Label];[Summary];[Description]",
                args=[None, None, None, None]
            )
        label = split_content[0].strip()
        summary = split_content[1].strip()
        desc = split_content[2].strip() + f"\nSubmitted by {submitter}"
        repo = bot.git.get_repo("iamdadbod/SpringCollab2020Issues")
        git_label = repo.get_label(find_label(label))
        issue = repo.create_issue(summary, body=desc, labels = [git_label])
        url = issue.html_url
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "Bug Submitted",
                "color": 53380,
                "fields": [
                    {
                        "name": summary,
                        "value": desc,
                        "inline": False
                    },
                    {
                        "name": "URL",
                        "value": url,
                        "inline": False
                    }
                ]
            }
        )

    @bot.command_on_message()
    def buglist(message):
        return message_data(
            message.channel,
            message="",
            embed={
                "title": "List of Issues",
                "description": "https://github.com/iamdadbod/SpringCollab2020Issues/issues",
                "color": 53380,
            }
        )
