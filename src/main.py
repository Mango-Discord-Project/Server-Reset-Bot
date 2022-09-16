from os import environ

from discord import (
    Intents,
    Forbidden,
    NotFound,
    HTTPException
    )
from discord.ext.commands import (
    Bot as DiscordBot,
    Context as Ctx,
    Command as Cmd,
    is_owner,
    GuildChannelConverter,
    RoleConverter,
    MemberConverter,
    EmojiConverter,
    GuildStickerConverter,
    CommandError,
    BadArgument
    )
from rich import print
from rich.console import Console
from dotenv import load_dotenv
import pretty_errors

load_dotenv()

class Bot(DiscordBot):
    def __init__(self):
        super().__init__(command_prefix='sr.', intents=Intents.all())
        self.delete_whitelist: dict[str, list[str]] = {
            'channel': [
                'lobby',
                ],
            'role': [],
            'member': [],
            'emoji': [],
            'sticker': []
        }
        self.converter: dict = {
            'channel': GuildChannelConverter(),
            'role': RoleConverter(),
            'member': MemberConverter(),
            'emoji': EmojiConverter(),
            'sticker': GuildStickerConverter()
        }
        self.console = Console()
        
        self._add_command()
    
    async def on_ready(self):
        self.console.log('Server Reset Bot Online')

    def _add_command(self):
        @is_owner()
        @self.command()
        async def delete(ctx: Ctx, item: str, *args) -> Cmd:
            if item == 'everything':
                return ...
            if item.removeprefix('all_') in self.delete_whitelist:
                if item.startswith('all_'):
                    item = item.removeprefix('all_')
                    self.console.log(f'Starting delete all_{item} from {ctx.guild.name}({ctx.guild.id})')
                    iter_list = getattr(ctx.guild, f'{item}s')
                else:
                    iter_list = []
                    for item_ in args:
                        try:
                            item = await self.converter[item].convert(ctx, item)
                        except BadArgument:
                            self.console.log(f'Error on convert {item} of {item_} from {ctx.guild.name}({ctx.guild.id}): The converter failed to convert the argument.')
                        except CommandError:
                            self.console.log(f'Error on convert {item} of {item_} from {ctx.guild.name}({ctx.guild.id}): A generic exception occurred when converting the argument.')
                        else:
                            self.console.log(f'Success on convert {item} of {item_} from {ctx.guild.name}({ctx.guild.id})')
                            iter_list.append(item)
                    self.console.log(f'Starting delete list of {item}, {iter_list}')

                for item_ in iter_list:
                    if item_.name in self.delete_whitelist[item]:
                        self.console.log(f'Skip delete for {item_}: item in delete_whitelist')
                        continue
                    if item_ is None:
                        self.console.log(f'Skip delete for {item_}: item is None')
                        continue
                    try:
                        reason=f'Server Reset Bot Delete, Executioner: {ctx.author}'
                        if item == 'member':
                            await item_.kick(reason=reason)
                        await item_.delete(reason=reason)
                    except Forbidden:
                        self.console.log(f'Error on delete {item_} from {item_.name}({item_.id}): Forbidden, You do not have proper permissions to delete the channel.')
                    except NotFound:
                        self.console.log(f'Error on delete {item_} from {item_.name}({item_.id}): NotFound, The channel was not found or was already deleted.')
                    except HTTPException:
                        self.console.log(f'Error on delete {item_} from {item_.name}({item_.id}): HTTPException, Deleting the channel failed.')
                    else:
                        self.console.log(f'Success on delete {item_} from {ctx.guild.name}({ctx.guild.id})')
                self.console.log(f'Finished on {item} from {ctx.guild.name}({ctx.guild.id})')
            else:
                self.console.log(f'Command argument: "item" error -> {item}')

bot = Bot()
bot.run(environ.get('TOKEN'))