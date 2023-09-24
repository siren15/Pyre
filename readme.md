# **Pyre**

### ![](https://autumn.revolt.chat/attachments/_2UsmLFHBOWEELm4Tzx-wJTusxWAf4RJuVHpUo8OBp/Pyre_20230629112501.png?width=100)

### **A** [**Revolt.chat**](https://revolt.chat) **API bot wrapper**

**This wrapper is a** **WIP**. Pyre is a fast and stable-ish wrapper for revolt.

I want to achieve a wrapper that will be stable, easy to use and understand.

**What works?**

- Caching and cache management of servers, users, members, roles, channels
- Raw methods for interacting with the API I deemed neccessary
- Recieving events from the API
- Sending messages, embeds, uploading to the API

**What needs to be done?**

- Adding methods to models
- Proper rate limiting and rate limit prevention
- Documentation
- Commands system
- Extension system
- Improvements, making stuff more efficient
- More stuff, idk...

---

**Example usage:**
`Python 3.10+ needed.`

```python
import os
import pyre.models as models
from pyre import PyreClient

bot = PyreClient('YOUR TOKEN HERE')


@bot.listen(models.ClientReady)
async def on_ready():
    print(f'{bot.user.username} fed to the Pyre!')
    latency = await bot.latency() * 1000
    print(f"Bot's latency: {latency:.0f}ms")


@bot.listen(models.Message)
async def send_message(message: models.Message):
    # example on building embeds, embeds don't have fields in revolt, but I'm thinking on adding a system like that that will use description
    if message.content == '+ina' and message.author.bot is False:
        embed = models.Embed()
        embed.title = "INA"
        embed.icon_url = "https://media.tenor.com/images/3b4e1e628bb5778cc1b27b66a3f6b5d3/tenor.gif"
        embed.media = 'tenor-3608348314.gif' # media field is uploading an image file to revolt, like an attachment
        embed.description = "INA"
        embed.colour = "#6d5f7b"
        await message.channel.send(embed=embed)


@bot.listen(models.MessageUpdate)
async def udpate_message(message: models.MessageUpdate):
    print(message.before)
    print(message.after)

@bot.listen(models.ServerRoleCreate)
async def memupd(event: models.ServerRoleCreate):
    print(event.before)
    print(event.after)

bot.start()
```
