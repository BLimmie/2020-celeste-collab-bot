import traceback

from src.tools.funcblocker import funcblocker
class CollabBot:
    def __init__(self, dbconn, client, config, git):
        self.command_on_message_list = {}
        # All necessary data
        self.conn = dbconn
        self.client = client
        self.config = config
        self.git = git

    async def send_message(self, message_info):
        """
        Sends message to channel in message_info
        """
        if message_info is None:
            return
        if message_info.message is None and message_info.embed is None:
            return
        if isinstance(message_info.channel, int):
            channel = self.client.get_channel(message_info.channel)
        else:
            channel = message_info.channel
        message = await channel.send(message_info.message, embed=message_info.embed)
        return message

    def command_on_message(self, timer=None, roles=None, positive_roles=True, coro=None):
        """
        Decorator for command_on_message function
        name of the function is the command YangBot looks for
        e.g.
        @bot.command_on_message(timer, roles, positive_roles, coro)
        def test(message):
            return message_data(0000000000, message.content, args, kwargs)
        procs on $test
        args:
        timer (timedelta) = time between procs
        roles (list of string) = role names to check
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        coro (coroutine) = coroutine to run after function finishes running
        secondary_args:
        func (function) = function to run, returns a message_data
        """

        def wrap(func):
            def wrapper(message):
                return func(message)

            self.command_on_message_list[func.__name__] = funcblocker(
                wrapper, timer, roles, positive_roles, coro)
            return wrapper

        return wrap

    async def run_command_on_message(self, message):
        """
        Precondition: message content starts with '$'
        """
        command = message.content.split()[0][1:]
        if command in self.command_on_message_list:
            try:
                message_info = self.command_on_message_list[command].proc(
                    message.created_at, message.author, message)
                send_message = await self.send_message(message_info)
                if self.command_on_message_list[command].coro is not None and message_info is not None:
                    await self.command_on_message_list[command].coro(send_message, *message_info.args,
                                                                     **message_info.kwargs)
            except Exception:
                traceback.print_exc()