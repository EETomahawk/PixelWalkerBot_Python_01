#Python 3.10
#Correct for PixelWalker v0.5.0-alpha

from datetime import datetime
import requests  #requests==2.31.0
import websocket #websocket-client==1.7.0
import json
import struct
from time import sleep
from threading import Thread

_print=print
def print(*args, **kwargs):
    _print(f"[{str(datetime.now().time())[:-3]}]",*args, **kwargs)

class Client:
    API_URL = "https://api.pixelwalker.net"
    WEBSOCKET_URL = "wss://game.pixelwalker.net"
    ROOM_TYPE = "pixelwalker3"

    class EventTypes:
        Ping      = 63  #0x3F = b"?"
        Message   = 107 #0x6B = b"k"

    class MessageTypes:
        PlayerInit          = 0
        UpdateRights        = 1
        WorldMetadata       = 2
        WorldCleared        = 3
        WorldReloaded       = 4
        WorldBlockPlaced    = 5
        ChatMessage         = 6
        SystemMessage       = 7
        PlayerJoined        = 8
        PlayerLeft          = 9
        PlayerMoved         = 10
        PlayerFace          = 11
        PlayerGodMode       = 12
        PlayerModMode       = 13
        PlayerCheckpoint    = 14
        PlayerRespawn       = 15
        PlayerReset         = 16
        PlayerCrown         = 17
        PlayerKeyPressed    = 18
        PlayerCounters      = 19
        PlayerWin           = 20
        PlayerLocalSwitchChanged    = 21
        PlayerLocalSwitchReset      = 22
        GlobalSwitchChanged         = 23
        GlobalSwitchReset           = 24

    def __init__(self):
        self.socket = None

    def joinRoom(self, authToken:str, roomID:str, onMessageCallback, onErrorCallback, onCloseCallback):
        url = f"{self.API_URL}/api/joinkey/{self.ROOM_TYPE}/{roomID}"
        roomToken = requests.get(url, headers={"Authorization":authToken}).json()["token"]
        self.socket = websocket.WebSocketApp(f"{self.WEBSOCKET_URL}/room/{roomToken}",
                                             on_message = onMessageCallback,
                                             on_error = onErrorCallback,
                                             on_close = onCloseCallback,
                                             on_data = onData)
        self.socket.run_forever()

    def disconnect(self):
        if self.socket: self.socket.close()

    # def send(self, *args):
    #     if not self.socket: print("Can't send - not connected.")
    #     else:
    #         try: self.socket.send(b"".join(args))
    #         except Exception as error:
    #             print('Send error', error)

#=======================================================================================================================

def loadConfig() -> dict:
    with open("./config.json", encoding="utf-8") as file:
        return json.load(file)

def onError(ws, error):
    print("onError", error)

def onClose(ws, code, reason):
    print("onClose", code, reason)

def onData(ws, data, opcode, _):
    print("onData opcode", opcode)

def onMessage(ws: websocket.WebSocketApp, message):
    buffer = bytearray(message)
    if buffer[0] == Client.EventTypes.Ping:
        ws.send(b'?', opcode=websocket.ABNF.OPCODE_BINARY)  #TODO
    elif not buffer[0] == Client.EventTypes.Message:
        print("Received unexpected message header type:", buffer[0])
        return
    match buffer[1]: #Assume message ID <128, else need to decode the varint.
        case Client.MessageTypes.PlayerInit:
            ws.send(b"\x6b\x00", opcode=websocket.ABNF.OPCODE_BINARY) #TODO
        case _:
            print("Received message type", buffer[1])

#=======================================================================================================================
config = loadConfig()
token = config["token"]
roomID = config["roomID"]

client = Client()
client.joinRoom(token, roomID, onMessage, onError, onClose)


# def read_7bit_int(buffer: bytes, offset: int) -> (int,int):
#     value = 0
#     shift = 0
#     byte = 0xFF
#
#     while byte & 0x80:
#         byte = buffer[offset]
#         value |= (byte & 0x7F) << shift
#         shift += 7
#         offset += 1
#
#     return value, offset
#
# def deserialize(buffer: bytes, offset: int) -> list:
#     arr = []
#     # types = []
#
#     while offset < len(buffer):
#         type_, o = read_7bit_int(buffer, offset)
#         length = None
#         offset = o
#
#         match type_:
#             case 0:  # String
#                 length, offset = read_7bit_int(buffer, offset)
#                 arr.append(buffer[offset:offset+length].decode('ascii'))
#                 offset += length
#             case 1:  # Byte
#                 arr.append(buffer[offset])
#                 offset += 1
#             case 2:  # Int16 (short)
#                 arr.append(int.from_bytes(buffer[offset:offset+2], byteorder='big', signed=True))
#                 offset += 2
#             case 3:  # Int32
#                 arr.append(int.from_bytes(buffer[offset:offset+4], byteorder='big', signed=True))
#                 offset += 4
#             case 4:  # Int64 (long)
#                 arr.append(int.from_bytes(buffer[offset:offset+8], byteorder='big', signed=True))
#                 offset += 8
#             case 5:  # Float
#                 arr.append(struct.unpack('>f', buffer[offset:offset+4])[0])
#                 offset += 4
#             case 6:  # Double
#                 arr.append(struct.unpack('>d', buffer[offset:offset+8])[0])
#                 offset += 8
#             case 7:  # Boolean
#                 arr.append(bool(buffer[offset]))
#                 offset += 1
#             case 8:  # ByteArray
#                 length, offset = read_7bit_int(buffer, offset)
#                 arr.append(buffer[offset:offset+length])
#                 offset += length
#
#         # types.append(type_)
#
#     # print(types)
#
#     return arr
