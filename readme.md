# CG's SRB2Kart Reader
This readme's mainly just a bow on top. If people actually want to use this I might make more a detailed readme later..

## Discord Usage:
* outputin \[#channel\] - changes the channel the bot will output in

## For your own server
This bot relies on the discord feature of Hostmod to view the log of your server. You could have this check any log file, though there are some srb2k-hostmod specific features built in.
* download and add [Hostmod](https://mb.srb2.org/threads/hostmod.26649/) to your server
* on your srb2k server, enable hostmod's discord feature `hm_discord On`
* <span style="color:red">Take note where hostmod creates discord-out files</span> (will be under `luafiles` at the root of your srb2k runtime folder)
* Make a discord bot
* Give your  bot the appropriate OAUTH2 permissions
    * applications.commands
    * send messages
    * use slash commands
* Copy down the token for your bot
* In a separate directory, git clone this repo `git clone https://github.com/cglitcher2/srb2k_discord_reader.git`
* cd to your cloned repo
* `source bin/activate`
* run cgreaderbot.py once. It will fail but that's ok `python cgreaderbot.py`
* look now for cgreaderconfig.json. Open it up
* Place your <span style="color:#3480eb">Discord Token</span> in between the quotes for field labeled `bot_token`
* For `filepattern`, we'll be making a pattern for the bot to match. It is: (<span style="color:red">the directory where the discord-out files are</span>) + discord-out*.txt
    * For example: `/home/cglitcher/.srb2kart/luafiles/discord-out*.txt`
    * `/home/cglitcher/.srb2kart/luafiles/` is the path where my discord-out files are
* Invite the bot to your discord server.
* now run the damn thing in tmux, screen, or equivalent
* Finally use the `outputin` slash command to tell the bot to put it in a specific channel

## Acknowledgements
Thanks for Tyron for the pointers and advice throughout the development of this.

Thanks to the Stray Banana discord for being great friends and giving inspiration.

For any questions, comments etc. I'm on discord: cglitcher#1172 😎