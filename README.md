**Disclaimer**: This bot is WIP and this repo tracks ongoing development. Some code may be buggy, and some information may be out of date.

### Introduction
Python implementation of a bot for PixelWalker, including low-level websocket/API stuff.

### Links
| Description              | URL                                                      |
|--------------------------|----------------------------------------------------------|
| PixelWalker Website      | https://pixelwalker.net/                                 |
| Block IDs                | [./blockIDs/README.md](./blockIDs/blockList)             |
| Room Types               | https://game.pixelwalker.net/listroomtypes               |
| Block Mappings           | https://game.pixelwalker.net/mappings                    |
| PixelWalker Forum Thread | https://forums.everybodyedits.com/viewtopic.php?id=48007 |
| PixelWalker Discord      | https://discord.com/invite/rDgtbbzDqX                    |

### Getting an authentication token for the bot
1. Go to the PixelWalker website and log in
2. Open developer tools (F12) and go to the **Network** tab
3. Refresh the website
4. Look for a file called `auth-refresh` near the bottom of the list and click on it
5. Under "Request Headers", find the "Authorization" key (see screenshot below)
6. The value of this key is your auth token. <u>**DO NOT SHARE IT!!**</u>
7. This token lasts for two weeks before expiring. You can check this using https://jwt.io/ 

<details>
<summary>Screenshot</summary>

![Finding the auth token](https://cdn.discordapp.com/attachments/1230093943941758977/1231626846005760131/image.png?ex=6627d2e2&is=66268162&hm=aca73c8570b63ce2ad7fddcf719373039d3e64207e9e0e8d09dba09ba3e1880f&)
</details>

### Websocket received data
*Source: Priddle, 2024-04-21*
> First byte of a websocket response is the header, this can either be 0x3F for a ping (which must be returned!) or 0x6B for a message.  
> If it's a message, second entry is a 7-bit encoded integer, which is the message type.
>
>After that comes the message data. Each entry starts with an entry type, which is a byte.  
>For strings and byte array entries, the data is prefixed with a length, which is also a 7-bit encoded integer.
>
>Byte order of entry values are big endian btw. World data byte array in init message is little endian (I forgot to change that, will do soon) 

#### Opcode
All websocket messages sent by the bot (init, ping, chat etc.) should use the BINARY opcode (0x02).
