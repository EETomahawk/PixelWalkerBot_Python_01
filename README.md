### Introduction
Python implementation of a bot for PixelWalker, including low-level websocket/API stuff.

1. PixelWalker forum thread: https://forums.everybodyedits.com/viewtopic.php?pid=799235#p799235
2. PixelWalker Discord: https://discord.com/invite/rDgtbbzDqX
3. Anatoly's JS bot used as reference: https://github.com/Anatoly03/pixelwalker.js/tree/main

### Message Buffer
*Source: Priddle*
> First byte of a websocket response is the header, this can either be 0x3F for a ping (which must be returned!) or 0x6B for a message.
>
>If it's a message, second entry is a 7-bit encoded integer, which is the message type.
>
>After that comes the message data. Each entry starts with an entry type, which is a byte.
>
>For strings and byte array entries, the data is prefixed with a length, which is also a 7-bit encoded integer.
>
>Byte order of entry values are big endian btw. World data byte array in init message is little endian (I forgot to change that, will do soon) 
