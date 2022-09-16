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
    is_owner
    )
from rich.console import Console
from dotenv import load_dotenv
import pretty_errors

load_dotenv()

class Bot(DiscordBot):
    def __init__(self):
        super().__init__(command_prefix='sr.', intents=Intents.all())
        self.delete_whitelist: dict = {
            'channel': 'lobby',
            'role': '',
            'member': '',
            'emoji': '',
            'sticker': ''
        }
        self.console = Console()
        self._add_command()
    
    async def on_ready(self):
        self.console.log('Server Reset Bot Online')
    
    async def _delete_all(self, ctx: Ctx, type_):
        if type_ not in self.delete_whitelist:
            return
        self.console.log(f'Starting delete all_{type_} from {ctx.guild.name}({ctx.guild.id})')
        for item in eval(f'ctx.guild.{type_}s'):
            if item.name in self.delete_whitelist[type_]:
                continue
                    
            try:
                reason=f'Server Reset Bot Delete, Executioner: {ctx.author}'
                if type_ == 'member':
                    await item.kick(reason=reason)
                await item.delete(reason=reason)
            except Forbidden:
                self.console.log(f'Error on delete {type_} from {item.name}({item.id}): Forbidden, You do not have proper permissions to delete the channel.')
            except NotFound:
                self.console.log(f'Error on delete {type_} from {item.name}({item.id}): NotFound, The channel was not found or was already deleted.')
            except HTTPException:
                self.console.log(f'Error on delete {type_} from {item.name}({item.id}): HTTPException, Deleting the channel failed.')
            else:
                self.console.log(f'Success on delete {type_} from {item.name}({item.id})')
            finally:
                self.console.log(f'Finished on {type_}')
        
        
    def _add_command(self):
        @is_owner()
        @self.command()
        async def delete(ctx: Ctx, item: str, *args) -> Cmd:
            match item:
                case 'everything':
                    ...
                case 'all_channel':
                    await self._delete_all(ctx, 'channel')
                case 'channels':
                    ...
                case 'all_role':
                    await self._delete_all(ctx, 'role')
                case 'roles':
                    ...
                case 'all_member':
                    await self._delete_all(ctx, 'member')
                case 'members':
                    ...
                case 'all_emoji':
                    await self._delete_all(ctx, 'emoji')
                case 'emojis':
                    ...
                case 'all_sticker':
                    await self._delete_all(ctx, 'sticker')
                case 'stickers':
                    ...
                case _:
                    self.console.log(f'Command argument: "item" error -> {item}')

bot = Bot()
bot.run(environ.get('TOKEN'))