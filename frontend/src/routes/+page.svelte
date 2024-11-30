<script lang="ts">
  import { connect, sendMessage } from "$lib/socket";

  const sendMsg = () => {
    const input = document.getElementById("message-field") as HTMLInputElement;
    const msg = input.value;
    sendMessage({ event: "message", message: msg });
  };
</script>

<input id="message-field" type="text" placeholder="Enter message" />
<button on:click={connect}>Connect to WebSocket</button>
<button on:click={sendMsg}>Send Message</button>
