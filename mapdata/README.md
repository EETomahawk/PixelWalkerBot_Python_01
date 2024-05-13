## Init Map Data
*13th May 2024 (PixelWalker v0.7.1-alpha).*  
Reference MartenM: https://github.com/MartenM/PixelPilot/blob/62739e6c6b082979fe30dd76445ffbfe195b9392/PixelPilotCore/PixelGameClient/Messages/Received/InitPacket.cs#L3

### Init Message
The following table lists the data in the init message. It assumes the raw websocket data has already been decoded into separate variables (Int32, byte array, string etc).

|ID|Type|Information|
|---|---|---|
|`0`|`Int32`|Player ID|
|`1`|`String`¹|Account ID|
|`2`|`String`|Username|
|`3`|`Int32`|Smiley ID|
|`4`|`Boolean`|Is Admin?|
|`5`|`Float64`|X Position|
|`6`|`Float64`|Y Position|
|`7`|`Boolean`|Can Edit?|
|`8`|`Boolean`|Can use God?|
|`9`|`String`|World Name|
|`10`|`Int32`|Play Count|
|`11`|`String`|Owner Username|
|`12`|`Byte Array`|Global Switch States|
|`13`|`Int32`|World Width|
|`14`|`Int32`|World Height|
|`15`|`Byte Array`|[Map Data](#deserialising-map-data)|

¹ Strings are UTF-8 encoded.

### Deserialising Map Data
Every block, left to right, top-down
0,0 is top-left

For each coord:
BG (Layer 0) block ID first (Int32)
Then FG (Layer 1) block ID.
Then optional addition args for special FG blocks:

Morphable: Int32 = morph/rotation ID. Coin/death door/gate numCoins, spike rotation, switch ID
Switch Resetter: Bool (byte) = Activated
Switch Activator: Int32, Bool = ID, status
Portal: Int32, Int32, Int32  = ID, target ID, rotation

|Index|X|Y|Type|Value|Description|
|---|---|---|---|---|---|
|`0`|`0`|`0`|`Int32`|`0`|BG Block ID¹ |
|`4`|`0`|`0`|`Int32`|`0`|FG Block ID²|
|`8`|`1`|`0`|`Int32`|`0`|Empty BG block|
|`12`|`1`|`0`|`Int32`|`0`|FG Block ID²|

¹Background (BG) is layer 0.  
²Foreground (FG) is layer 1.


|Offset|Type|Value|Description|
|---|---|---|---|
|`n`|`Int32`|`26`|Coin Door BlockID|
|`n+1`|`Int32`|`42`|42 coins required.|

|Y\X|0|1|2|
|---|---|---|---|
![.](../blockIDs/images/gravity_dot.png)

**3x3 world example:**  
Empty, Dot, bricks_green_bg  
Coin door, Spike, Purple Switch  
Switch resetter, portal, switch activator
