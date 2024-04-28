//Message IDs and onInitializedMessage() function from PixelWalker client JS, v0.5.0-alpha
//Useful for understanding received messages.

var V = (n=>(
n[n.PlayerInit = 0] = "PlayerInit",
n[n.UpdateRights = 1] = "UpdateRights",
n[n.WorldMetadata = 2] = "WorldMetadata",
n[n.WorldCleared = 3] = "WorldCleared",
n[n.WorldReloaded = 4] = "WorldReloaded",
n[n.WorldBlockPlaced = 5] = "WorldBlockPlaced",
n[n.ChatMessage = 6] = "ChatMessage",
n[n.SystemMessage = 7] = "SystemMessage",
n[n.PlayerJoined = 8] = "PlayerJoined",
n[n.PlayerLeft = 9] = "PlayerLeft",
n[n.PlayerMoved = 10] = "PlayerMoved",
n[n.PlayerFace = 11] = "PlayerFace",
n[n.PlayerGodMode = 12] = "PlayerGodMode",
n[n.PlayerModMode = 13] = "PlayerModMode",
n[n.PlayerCheckpoint = 14] = "PlayerCheckpoint",
n[n.PlayerRespawn = 15] = "PlayerRespawn",
n[n.PlayerReset = 16] = "PlayerReset",
n[n.PlayerCrown = 17] = "PlayerCrown",
n[n.PlayerKeyPressed = 18] = "PlayerKeyPressed",
n[n.PlayerCounters = 19] = "PlayerCounters",
n[n.PlayerWin = 20] = "PlayerWin",
n[n.PlayerLocalSwitchChanged = 21] = "PlayerLocalSwitchChanged",
n[n.PlayerLocalSwitchReset = 22] = "PlayerLocalSwitchReset",
n[n.GlobalSwitchChanged = 23] = "GlobalSwitchChanged",
n[n.GlobalSwitchReset = 24] = "GlobalSwitchReset",
n))(V || {});

onInitializedMessage(t) {
        switch (t.type) {
        case V.UpdateRights:
            this.canEdit = t.getBoolean(0),
            this.canToggleGodMode = t.getBoolean(1),
            this.ui.updateRights(),
            this.worldRenderer.updateAllChunks([N.AbovePlayers, N.Foreground]);
            break;
        case V.ChatMessage:
            {
                const i = t.getInt32(0)
                  , r = wi.Filter(t.getString(1))
                  , s = this.playersIncludingMe.find(o=>o.id === i);
                s && (this.ui.sideBar.chat.addMessage(s.username, r, s.usernameColor),
                s.addChatBubble(r))
            }
            break;
        case V.WorldMetadata:
            {
                const i = t.getString(0)
                  , r = t.getInt32(1)
                  , s = t.getString(2);
                this.ui.sideBar.updateMeta(i, r, s)
            }
            break;
        case V.WorldCleared:
            this.world.clear();
            break;
        case V.PlayerJoined:
            {
                let i = 0;
                const r = new rn(this,!1);
                r.id = t.getInt32(i++),
                r.connectUserId = t.getString(i++),
                r.username = t.getString(i++),
                r.face = t.getInt32(i++),
                r.isAdmin = t.getBoolean(i++),
                r.x = t.getDouble(i++),
                r.y = t.getDouble(i++),
                r.counters.goldCoins = t.getInt32(i++),
                r.counters.blueCoins = t.getInt32(i++),
                r.counters.deaths = t.getInt32(i++),
                r.isInGodMode = t.getBoolean(i++),
                r.isInModMode = t.getBoolean(i++),
                t.getBoolean(i++) === !0 && (this.crownPlayer = r),
                r.switches = t.getByteArray(i++),
                r.mountUsernameLabel(),
                this.players.push(r),
                this.ui.sideBar.playerList.addPlayer(r),
                r.initialized = !0
            }
            break;
        case V.PlayerLeft:
            {
                const i = t.getInt32(0)
                  , r = this.players.findIndex(s=>s.id === i);
                r !== -1 && (this.players[r].unmountUsernameLabel(),
                this.players[r].clearChatBubbles(),
                this.ui.sideBar.playerList.removePlayer(this.players[r]),
                this.players.splice(r, 1))
            }
            break;
        case V.PlayerMoved:
            {
                const i = t.getInt32(0)
                  , r = this.players.find(s=>s.id === i);
                r && (r.x = t.getDouble(1),
                r.y = t.getDouble(2),
                r.speedX = t.getDouble(3),
                r.speedY = t.getDouble(4),
                r.modifierX = t.getDouble(5),
                r.modifierY = t.getDouble(6),
                r.horizontal = t.getInt32(7),
                r.vertical = t.getInt32(8),
                r.spaceDown = t.getBoolean(9),
                r.spaceJustDown = t.getBoolean(10),
                r.tickId = t.getInt32(11),
                r.isDead = !1)
            }
            break;
        case V.PlayerFace:
            {
                const i = t.getInt32(0)
                  , r = this.playersIncludingMe.find(s=>s.id === i);
                r && (r.face = t.getInt32(1),
                r === this.player && (G.lastPlayerFace = r.face,
                this.ui.updateSmileyButton()))
            }
            break;
        case V.PlayerGodMode:
            {
                const i = t.getInt32(0)
                  , r = this.playersIncludingMe.find(s=>s.id === i);
                r && (r.isInGodMode = t.getBoolean(1),
                r === this.player && (this.ui.updateGodModeButton(),
                this.worldRenderer.updateAllChunks([N.Foreground])))
            }
            break;
        case V.PlayerModMode:
            {
                const i = t.getInt32(0)
                  , r = this.playersIncludingMe.find(s=>s.id === i);
                r && (r.isInModMode = t.getBoolean(1),
                r === this.player && this.worldRenderer.updateAllChunks([N.Foreground]))
            }
            break;
        case V.WorldBlockPlaced:
            {
                const i = t.getInt32(0)
                  , r = t.getInt32(1)
                  , s = t.getInt32(2)
                  , o = t.getInt32(3);
                this.world.setBlockData(i, r, s, this.getBlockDataFromMessage(o, t))
            }
            break;
        case V.PlayerCrown:
            this.crownPlayer = this.playersIncludingMe.find(i=>i.id === t.getInt32(0));
            break;
        case V.PlayerKeyPressed:
            this.keys.activateKey(t.getByte(0));
            break;
        case V.PlayerCheckpoint:
            {
                const i = t.getInt32(0)
                  , r = t.getInt32(1);
                this.checkPoint = new Ri(i,r),
                this.worldRenderer.updateAllChunks([N.Foreground])
            }
            break;
        case V.PlayerRespawn:
            {
                const i = t.getInt32(0)
                  , r = t.getInt32(1)
                  , s = t.getInt32(2)
                  , o = this.playersIncludingMe.find(l=>l.id === i);
                o && o.respawn(r, s)
            }
            break;
        case V.PlayerCounters:
            {
                const i = t.getInt32(0)
                  , r = this.players.find(s=>s.id === i);
                r && (r.counters.goldCoins = t.getInt32(1),
                r.counters.blueCoins = t.getInt32(2),
                r.counters.deaths = t.getInt32(3))
            }
            break;
        case V.PlayerReset:
            {
                const i = t.getInt32(0)
                  , r = this.playersIncludingMe.find(s=>s.id === i);
                if (r) {
                    const s = t.getInt32(1)
                      , o = t.getInt32(2);
                    r.reset(s, o),
                    r.isMe && this.reset()
                }
            }
            break;
        case V.WorldReloaded:
            console.log("World reloaded."),
            new sn(this.world).deserialize(t.getByteArray(0)),
            this.worldRenderer.updateAllChunks(),
            this.ui.minimap.reset();
            break;
        case V.PlayerLocalSwitchChanged:
            {
                const i = t.getInt32(0)
                  , r = this.players.find(s=>s.id === i);
                if (r) {
                    const s = t.getInt32(1)
                      , o = t.getByte(2);
                    r.switches[s] = o
                }
            }
            break;
        case V.PlayerLocalSwitchReset:
            {
                const i = t.getInt32(0)
                  , r = t.getByte(1)
                  , s = this.players.find(o=>o.id === i);
                s && s.switches.fill(r)
            }
            break;
        case V.GlobalSwitchChanged:
            {
                const i = t.getInt32(1)
                  , r = t.getByte(2);
                this.switches[i] = r,
                this.worldRenderer.updateAllChunks([N.Foreground])
            }
            break;
        case V.GlobalSwitchReset:
            {
                const i = t.getByte(1);
                this.switches.fill(i),
                this.worldRenderer.updateAllChunks([N.Foreground])
            }
            break
        }
    }