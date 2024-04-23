//Sourced from https://bg0gwwg.116.202.52.27.sslip.io/assets/game-Z4JOaMqb.js, v0.4.1-alpha
onInitializedMessage(t)
{
    switch (t.type) {
    case $.UpdateRights:
        this.canEdit = t.getBoolean(0),
        this.canToggleGodMode = t.getBoolean(1),
        this.ui.updateRights(),
        this.worldRenderer.updateAllChunks([W.AbovePlayers, W.Foreground]);
        break;
    case $.ChatMessage:
        {
            const i = t.getInt32(0)
              , r = pi.Filter(t.getString(1))
              , n = this.allPlayers.find(o=>o.id === i);
            n && (this.ui.sideBar.chat.addMessage(n.username, r, n.usernameColor),
            n.addChatBubble(r))
        }
        break;
    case $.WorldMetadata:
        {
            const i = t.getString(0)
              , r = t.getInt32(1)
              , n = t.getString(2);
            this.ui.sideBar.updateMeta(i, r, n)
        }
        break;
    case $.WorldCleared:
        this.world.clear();
        break;
    case $.PlayerJoined:
        {
            let i = 0;
            const r = new Vn(this,!1);
            r.id = t.getInt32(i++),
            r.connectUserId = t.getString(i++),
            r.username = t.getString(i++),
            r.face = t.getInt32(i++),
            r.isAdmin = t.getBoolean(i++),
            r.x = t.getDouble(i++),
            r.y = t.getDouble(i++),
            r.isInGodMode = t.getBoolean(i++),
            r.isInModMode = t.getBoolean(i++),
            t.getBoolean(i++) && (this.crownPlayer = r),
            r.mountUsernameLabel(),
            this.players.push(r),
            this.ui.sideBar.playerList.addPlayer(r)
        }
        break;
    case $.PlayerLeft:
        {
            const i = t.getInt32(0)
              , r = this.players.findIndex(n=>n.id === i);
            r !== -1 && (this.players[r].unmountUsernameLabel(),
            this.players[r].clearChatBubbles(),
            this.ui.sideBar.playerList.removePlayer(this.players[r]),
            this.players.splice(r, 1))
        }
        break;
    case $.PlayerMoved:
        {
            const i = t.getInt32(0)
              , r = this.players.find(n=>n.id === i);
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
            r.counters.goldCoins = t.getInt32(12),
            r.counters.blueCoins = t.getInt32(13),
            r.isDead = !1)
        }
        break;
    case $.PlayerFace:
        {
            const i = t.getInt32(0)
              , r = this.allPlayers.find(n=>n.id === i);
            r && (r.face = t.getInt32(1),
            r === this.player && (O.lastPlayerFace = r.face,
            this.ui.updateSmileyButton()))
        }
        break;
    case $.PlayerGodMode:
        {
            const i = t.getInt32(0)
              , r = this.allPlayers.find(n=>n.id === i);
            r && (r.isInGodMode = t.getBoolean(1),
            r === this.player && (this.ui.updateGodModeButton(),
            this.worldRenderer.updateAllChunks([W.Foreground])))
        }
        break;
    case $.PlayerModMode:
        {
            const i = t.getInt32(0)
              , r = this.allPlayers.find(n=>n.id === i);
            r && (r.isInModMode = t.getBoolean(1),
            r === this.player && this.worldRenderer.updateAllChunks([W.Foreground]))
        }
        break;
    case $.PlaceBlock:
        {
            const i = t.getInt32(0)
              , r = t.getInt32(1)
              , n = t.getInt32(2)
              , o = t.getInt32(3);
            this.world.setBlockData(i, r, n, this.getBlockDataFromMessage(o, t))
        }
        break;
    case $.CrownTouched:
        this.crownPlayer = this.allPlayers.find(i=>i.id === t.getInt32(0));
        break;
    case $.KeyPressed:
        this.keys.activateKey(t.getByte(0));
        break;
    case $.PlayerCheckpoint:
        {
            const i = t.getInt32(0)
              , r = t.getInt32(1);
            this.checkPoint = new Pi(i,r),
            this.worldRenderer.updateAllChunks([W.Foreground])
        }
        break;
    case $.PlayerRespawn:
        {
            const i = t.getInt32(0)
              , r = t.getInt32(1)
              , n = t.getInt32(2)
              , o = this.allPlayers.find(l=>l.id === i);
            o && o.respawn(r, n)
        }
        break
    }
}