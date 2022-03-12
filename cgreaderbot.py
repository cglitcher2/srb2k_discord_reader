import os,sys,glob,json,shutil
import signal
import discord
from discord.ext import tasks, commands
from discord import Option, SlashCommandOptionType


class ReaderBot(discord.Bot):
    def __init__(self,config, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self.target_channel = None
        self.config = config

    def set_target_channel(self,channel_id):
        self.target_channel = self.get_channel(channel_id)
        self.config['default_channel'] = channel_id

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        default_channel_id = None
        if 'default_channel' not in self.config or self.config['default_channel'] is None:
            for guild in self.guilds:
                for channel in guild.text_channels: #getting only text channels
                    if channel.permissions_for(guild.me).send_messages: #checking if you have permissions
                        default_channel_id = channel.id
                        break
        else:
            default_channel_id = self.config['default_channel']

        if default_channel_id is None:
            msg = f"Unable to find a channel I can print in!"
            raise RuntimeError(msg)

        await self.get_channel(default_channel_id).send('👀 hello I am here')
        self.set_target_channel(default_channel_id)


class FileEventHandler(commands.Cog):
    def __init__(self, bot,filepattern,cfg_file):
        self.bot = bot
        self.filepattern = filepattern
        self.target_file = self.get_most_recent_file(filepattern)
        self.offset = 0
        self.cfg_file = cfg_file
        self.printer.start()
        self.save_config.start()

    def cog_unload(self):
        self.printer.cancel()
        self.save_config.cancel()


    def get_most_recent_file(self,filepattern):
        files = glob.glob(filepattern)
        target_file = max(files,key=os.path.getctime)
        return target_file

    def process_text(self,new_data):
        outtext = ""

        text = new_data.strip()
        # Replace ||| with newlines
        for line in text.split("\n"):
            if line.startswith("**Result -"):
                line = line.replace("|||","\n")

            outtext += line + "\n"

        return outtext

    #Save the config for the bot every once in a while
    @tasks.loop(seconds = 60.0)
    async def save_config(self):
        with open(self.cfg_file,'w') as f:
            print(json.dumps(self.bot.config),file=f)

    #main loop function: 
    # Check if any new data has arrived in the last known output file
    # Check if a new file has been created
    # Output new text from both files
    @tasks.loop(seconds=5.0)
    async def printer(self):
        if self.bot.target_channel is None:
            return

        outtext = ""

        #first find out if the server has restarted since last loop (a new file will be created)
        files = glob.glob(self.filepattern)
        most_recent_file = max(files,key=os.path.getctime)
        if most_recent_file != self.target_file:
            #Yes, new file. proccess the rest of what the old file has, and put it on this output batch
            with open(self.target_file,'r') as oldfp:
                oldfp.seek(self.offset)
                remaining_text = oldfp.read()
                
            outtext += self.process_text(remaining_text)
            #Set up for the next file
            outtext += "*~~~~~~~~~~Server has restarted~~~~~~~~~~*\n"
            self.target_file = most_recent_file
            self.offset = 0

        # Next get the new data from the most recent file        
        with open(most_recent_file,'r') as f:
            f.seek(self.offset)
            new_data = f.read()
            self.offset += len(new_data)

        outtext += self.process_text(new_data)

        #Don't send empty strings else we get an error
        if outtext.strip() == "":
            return

        print(f"new_data:{outtext}")
        await self.bot.target_channel.send(outtext)

    @printer.before_loop
    @save_config.before_loop
    async def before_printer(self):
        print('waiting for bot to initialize...')
        await self.bot.wait_until_ready()


#Setup configurations
def loadcfg(cfglocation = 'cgreaderconfig.json'):
    if not os.path.isfile(cfglocation):
        msg = f"No config file {cfglocation} found! I've made a config file at {cfglocation} with a template of what should be filled out."
        shutil.copyfile("cgreaderconfig_template.json",cfglocation)
        raise RuntimeError(msg)

    with open(cfglocation,'r') as f:
        cfg = json.loads(f.read())
        
    required = ['filepattern','bot_token']

    for field in required:
        if field not in cfg:
            msg = f"missing required config {field} in cfg file {cfglocation}. See cgreaderconfig_template.json for description."
            raise RuntimeError(msg)

        if cfg[field] is None:
            msg = f"required config {field} in cfg file {cfglocation} is null. See cgreaderconfig_template.json for description."
            raise RuntimeError(msg)

    return cfg


if __name__ == "__main__":
    #user may specify a different config file
    cfg_file = 'cgreaderconfig.json' if len(sys.argv) < 2 else sys.argv[1]
    cfg = loadcfg(cfg_file)
    filepattern = cfg["filepattern"]
    TOKEN = cfg["bot_token"]

    bot = ReaderBot(cfg)
    bgcog = FileEventHandler(bot,filepattern,cfg_file)

    #Slash command for setting output channel. I have no idea how to do with within the child class 🤷‍♀️
    @bot.slash_command(name='outputin', description='Tell CG bot where to output its messages')
    async def greet(ctx, channel: Option(SlashCommandOptionType.channel,required=True)):
        bot.set_target_channel(channel.id)
        await ctx.respond(f'Ok! I will now output in {channel.mention}')
    
    bot.run(TOKEN)




