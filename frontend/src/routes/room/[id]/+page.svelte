<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { awaitMessage, connect, sendMessage } from "$lib/socket";
  import { browser } from "$app/environment";

  export let data: { props: { id: string } };
  const id: string = data.props.id;

  let roomData: {} | null = null;
  let alias: string | null = null;
  let isHost = false;

  function sendLeaveRoomMessage() {
    if (browser) {
      sendMessage({
        event: "leave-room",
        message: JSON.stringify({ id: id }),
      });
    }
  }

  function handleBeforeUnload(event: BeforeUnloadEvent) {
    sendLeaveRoomMessage();
  }

  async function handleMessage(message: { event: string; message: any }) {
    console.log("Received message:", message);
    switch (message.event) {
      case "room-data":
        roomData = JSON.parse(message.message);
        break;
      case "room-joined":
        const d = JSON.parse(message.message);
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
        await handleMessage(x);
        break;
      case "user-left":
        sendMessage({
          event: "get-room",
          message: id,
        });
        let y = await awaitMessage();
        await handleMessage(y);
        break;
      default:
        console.error("Unexpected event:", message.event);
    }
  }

  onMount(() => {
    if (browser) {
      // Redirect to home page if alias is not provided
      const params = new URLSearchParams(window.location.search);
      alias = params.get("alias");
      let is_host = params.get("host");
      if (!alias) {
        window.location.href = "/";
      }
      if (!is_host) {
        is_host = "false";
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
              type: is_host == "true" ? "host" : "guest",
            }),
          });
          console.log("Joined room");
          const data = await awaitMessage();
          console.log("Received message:", data);

          switch (data.event) {
            case "room-not-found":
              roomData = data.message;
              break;
            case "room-data":
              roomData = data.message;
              break;
            case "room-joined":
              const d = JSON.parse(data.message);
              console.log(d);
              roomData = d.room;
              alias = d.alias;
              isHost = d.isHost;
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
</script>

<h1>Room</h1>
<h2 id="roomId">Room ID: {id}</h2>
<h2 id="roomData">Room Data: {JSON.stringify(roomData)}</h2>
<h2 id="alias">Alias: {alias}</h2>
<h2 id="isHost">Is Host: {isHost}</h2>
