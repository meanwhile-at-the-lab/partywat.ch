<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { awaitMessage, connect, sendMessage } from "$lib/socket";
  import { browser } from "$app/environment";
  import YouTubePlayer from "./YouTubePlayer.svelte";

  let player: YouTubePlayer;

  export let data: { props: { id: string } };
  const id: string = data.props.id;

  let roomData: {} | null = null;
  let alias: string | null = null;
  let isHost = false;
  let hostCredential: string | null = null;

  function sendLeaveRoomMessage() {
    if (browser) {
      sendMessage({
        event: "leave-room",
        message: JSON.stringify({ id: id }),
      });
    }
  }

  function hostStatusChange() {
    player.setControlsVisibility(isHost);
  }

  $: if (isHost) {
    hostStatusChange();
  }

  function handleBeforeUnload() {
    sendLeaveRoomMessage();
  }

  async function handleMessage(message: { event: string; message: any }) {
    console.log("Received message:", Object.keys(message as object));
    try {
      message = JSON.parse(message as unknown as string);
    } catch (err) {}
    if (typeof message.message === "string") {
      try {
        message.message = JSON.parse(message.message);
      } catch (err) {}
    }

    switch (message.event) {
      case "room-data":
        roomData = message.message;
        break;
      case "room-joined":
        const d = message.message;
        roomData = d.room;
        alias = d.alias;
        isHost = d.isHost;
        break;

      case "user-joined":
        sendMessage({
          event: "get-room",
          message: id,
        });
        let x = await awaitMessage();
        console.log("Received message (user-joined):", x);
        await handleMessage(x);
        break;
      case "user-left":
        sendMessage({
          event: "get-room",
          message: id,
        });
        let y = await awaitMessage();
        console.log("Received message (user-left):", y);
        await handleMessage(y);
        break;
      case "video-data":
        player.handleVideoData(message.message);
        break;
      default:
        console.error("Unexpected event:", message);
    }
  }
  onMount(() => {
    if (browser) {
      // Redirect to home page if alias is not provided
      const params = new URLSearchParams(window.location.search);
      alias = params.get("alias");
      hostCredential = params.get("cred") || null;
      let is_host = params.get("type");
      if (!alias) {
        window.location.href = "/";
      }
      if (!is_host) {
        is_host = "guest";
      }

      (async () => {
        try {
          await connect();
          console.log("Connected");
          await sendMessage({
            event: "join-room",
            message: JSON.stringify({
              id: id,
              alias: alias,
              type: is_host,
              hostCredential: hostCredential,
            }),
          });
          console.log("Joined room");
          let data = await awaitMessage();
          data = JSON.parse(data as unknown as string);

          switch (data.event) {
            case "room-not-found":
              roomData = data.message;
              break;
            case "room-joined":
              const d = data.message;
              console.log(d);
              roomData = d.room;
              alias = d.alias;
              isHost = d.isHost;
              console.log("isHost:", isHost); // Log isHost value
              console.log("isHost:", isHost); // Log isHost value
              break;
            default:
              console.error("Unexpected event:", data.event);
          }
        } catch (err) {
          console.error(err);
        }
      })().then(async () => {
        // Wait for more messages
        while (true) {
          const data = await awaitMessage();
          console.log("0_Received message:", data);
          await handleMessage(data);
        }
      });

      // Add event listener for beforeunload
      window.addEventListener("beforeunload", handleBeforeUnload);
    }
  });

  onDestroy(() => {
    if (browser) {
      // Remove the event listener
      window.removeEventListener("beforeunload", handleBeforeUnload);
      // Send the leave-room message
      sendLeaveRoomMessage();
    }
  });

  function videoSeek(p: YT.Player) {
    console.log("videoSeek called"); // Log function call
    if (isHost) {
      console.log("Sent seek to", p.getCurrentTime());
      sendMessage({
        event: "video-seek",
        message: JSON.stringify({
          id: id,
          timestamp: p.getCurrentTime(),
          hostCredential: hostCredential, // Send host credential
        }),
      });
    }
  }

  function videoPaused(player: YT.Player) {
    console.log("videoPaused called"); // Log function call
    if (isHost) {
      sendMessage({
        event: "video-paused",
        message: JSON.stringify({
          id: id,
          is_paused: player.getPlayerState() === YT.PlayerState.PAUSED,
          hostCredential: hostCredential, // Send host credential
        }),
      });
    }
  }
</script>

<h1>Room</h1>
<h2 id="roomId">Room ID: {id}</h2>
<h2 id="roomData">Room Data: {JSON.stringify(roomData)}</h2>
<h2 id="alias">Alias: {alias}</h2>
<h2 id="isHost">Is Host: {isHost}</h2>

<YouTubePlayer
  bind:this={player}
  onseek={videoSeek}
  onpause={videoPaused}
  videoId="dQw4w9WgXcQ"
/>
