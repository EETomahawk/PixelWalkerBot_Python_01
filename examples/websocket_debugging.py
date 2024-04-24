#Correct as of 2024-04-24
import os
os.environ["SSLKEYLOGFILE"] = "./secrets.log"
#Now connect the bot websocket to generate the secrets.log.
#Run Wireshark. Set Edit > Preferences > Protocols > TLS > (Pre)-Master-Secret log filename to the above file.
#Start Wireshark logging and filter by the IP address of the Pixelwalker website (get IP by pinging pixelwalker.net).
#Send/receive some messages using the websocket.
#Wireshark will automatically decrypt the TLS-encrypted websocket traffic.
