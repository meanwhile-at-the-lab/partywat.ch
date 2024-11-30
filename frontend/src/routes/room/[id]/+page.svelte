<script lang="ts">
  export let data: { id: string };
  import { awaitMessage, connect, sendMessage } from "$lib/socket";
  const id: string = data.props.id;

  let roomData = null;

  // Get room data

  (async () => {
    try {
      await connect();
      sendMessage({ event: "get-room", message: id });
      const data = await awaitMessage();
      switch (data["event"]) {
        case "room-data":
          roomData = data.message;
          break;
        case "room-not-found":
          roomData = "Room not found";
          break;
        default:
          console.error("Unexpected event", data, data["event"]);
      }
      console.log("DATA", data);
    } catch (err) {
      console.error(err);
    }
  })();
</script>

<h1>Room</h1>
<h2>Room ID: {id}</h2>
<h2>Room Data: {roomData}</h2>
