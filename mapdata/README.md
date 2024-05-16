## Init Map Data
*13th May 2024 (PixelWalker v0.7.1-alpha).*  
Reference MartenM: https://github.com/MartenM/PixelPilot/blob/62739e6c6b082979fe30dd76445ffbfe195b9392/PixelPilotCore/PixelGameClient/Messages/Received/InitPacket.cs#L3

### Init Message
The following table lists the data in the init message. It assumes the raw websocket data has already been decoded into separate variables (Int32, byte array, string etc).

|ID|Type|Information|
|---|---|---|
|0|`Int32`|Player ID|
|1|`String`¹|Account ID|
|2|`String`|Username|
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

![3x3_example.png](./images/3x3_example.png)

The following table unpacks the mapdata byte array for a theoretical 3x3 world containing the block in the image above. Additional information for special blocks (switches, portals etc.) is highlighted in green.

|Index|X|Y|Type|Value|Description|
|---|---|---|---|---|---|
|`0-3`|0|0|`Int32`|0|Empty BG block ID|
|`4-7`|0|0|`Int32`|0|Empty FG block ID|
|`8-11`|1|0|`Int32`|0|Empty BG block ID|
|`12-15`|1|0|`Int32`|5|Dot block ID|
|`16-19`|2|0|`Int32`|94|Green Brick BG block ID|
|`20-23`|2|0|`Int32`|0|Empty FG block ID|
|`24-27`|0|1|`Int32`|0|Empty BG block ID|
|`28-31`|0|1|`Int32`|5|Coin Door block ID|
|`32-35`|0|1|`Int32`|9|$\color{lime}{\textsf{Number of coins required}}$|
|`36-39`|1|1|`Int32`|0|Empty BG block ID|
|`40-43`|1|1|`Int32`|45|Spikes block ID|
|`44-47`|1|1|`Int32`|0|$\color{lime}{\textsf{Spike rotation}}$¹|
|`48-51`|2|1|`Int32`|0|Empty BG block ID|
|`52-55`|2|1|`Int32`|33|Purple Switch block ID|
|`56-59`|2|1|`Int32`|5|$\color{lime}{\textsf{Purple Switch ID}}$|
|`60-63`|0|2|`Int32`|0|Empty BG block ID
|`64-67`|0|2|`Int32`|35|Purple Switch Resetter block ID|
|`68`|0|2|`Boolean`|False|$\color{lime}{\textsf{Purple Switch Resetter ON/OFF}}$²|
|`69-72`|1|2|`Int32`|0|Empty BG block ID|
|`73-76`|1|2|`Int32`|16|Portal block ID|
|`77-80`|1|2|`Int32`|3|$\color{lime}{\textsf{Portal rotation}}$³|
|`81-84`|1|2|`Int32`|16|$\color{lime}{\textsf{ID of portal}}$|
|`85-88`|1|2|`Int32`|16|$\color{lime}{\textsf{Target ID of portal}}$|
|`89-92`|2|2|`Int32`|0|Empty BG block ID|
|`93-96`|2|2|`Int32`|33|Purple Switch Activator block ID|
|`97-100`|2|2|`Int32`|5|$\color{lime}{\textsf{Purple Switch Activator switch ID}}$|
|`101`|2|2|`Boolean`|True|$\color{lime}{\textsf{Purple Switch Activator ON/OFF}}$²|

¹Rotation IDs:

|¹Rotation ID|Examples|
|:---:|---|
|0|![3x3_example.png](./images/rot0.png)|
|1|![3x3_example.png](./images/rot1.png)|
|2|![3x3_example.png](./images/rot2.png)|
|3|![3x3_example.png](./images/rot3.png)|

e.g. 
²False = OFF  
³Portal rotation IDs are ???  
⁴  
⁵


