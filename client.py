#Python 3.10
from pocketbase import PocketBase #pocketbase==0.10.1
import websocket #websocket-client==1.7.0
import json
import struct

class Client:
    API_ACCOUNT_LINK = "https://lgso0g8.116.202.52.27.sslip.io"
    API_ROOM_LINK = "wss://po4swc4.116.202.52.27.sslip.io"
    ROOM_TYPE = "pixelwalker2"

    class EventTypes:
        Ping      = 63  #0x3F = "?"
        Message   = 107 #0x6B = "k"

    class MessageTypes:
        init             = 0
        updateRights     = 1
        worldMetadata    = 2
        worldCleared     = 3
        chatMessage      = 4
        systemMessage    = 5
        playerJoined     = 6
        playerLeft       = 7
        playerMoved      = 8
        playerFace       = 9
        playerGodMode    = 10
        playerModMode    = 11
        playerCheckpoint = 12
        playerRespawn    = 13
        placeBlock       = 14
        crownTouched     = 15
        keyPressed       = 16

    def __init__(self):
        self.client = PocketBase(self.API_ACCOUNT_LINK)
        self.socket = None

    def createJoinRoom(self, authToken:str, worldID:str, onMessageCallback, onErrorCallback, onCloseCallback):
        self.client.auth_store.save(authToken)
        response = self.client.send(f"/api/joinkey/{self.ROOM_TYPE}/{worldID}", {})
        #print("PocketBase response", response)
        token = response["token"]
        self.socket = websocket.WebSocketApp(f"{self.API_ROOM_LINK}/room/{token}",
                                             on_message = onMessageCallback,
                                             on_error = onErrorCallback,
                                             on_close = onCloseCallback)
        self.socket.run_forever()

    def disconnect(self):
        if self.socket: self.socket.close()

    def send(self, *args):
        if not self.socket: print("Can't send - not connected.")
        else:
            try: self.socket.send(b"".join(args))
            except Exception as error:
                print('Send error', error)

    # def magic(value):
    #     return struct.pack('B', value)

#=======================================================================================================================

def loadConfig() -> dict:
    with open("./config.json", encoding="utf-8") as file:
        return json.load(file)

def onError(ws, error):
    print("onError", error)

def onClose(ws, code, reason):
    print("onClose", code, reason)

def onMessage(ws: websocket.WebSocketApp, message):
    buffer = bytearray(message)
    match buffer[0]:
        case Client.EventTypes.Ping:
            print("Received ping")
            ws.send(bytes([Client.EventTypes.Ping])) #TODO not working.

        case Client.EventTypes.Message:
            print()
            match buffer[1]: #Assume <=128, else need to varint decode.
                case Client.MessageTypes.init:
                    print("Received init")
                    client.send(b"\x6B",b"\x01",b"\x00") #TODO no effect
                    #await this.send(Magic(0x6B), Bit7(MessageType['init']))
            pass
        case _:
            print("onMessage unexpected header", buffer[0])

# def accept_event(self, buffer):
#     event_id, offset = read7BitInt(buffer, 0)
#     event_name = next((k for k, v in MessageType.items() if v == event_id), None)
#     data = deserialise(buffer, offset)
#     self.emit(event_name, data)

#def readEventBuffer(self, buffer)
#=======================================================================================================================
config = loadConfig()
token = config["token"]
roomID = config["roomID"]

client = Client()
client.createJoinRoom(token, roomID, onMessage, onError, onClose)

#
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
