<script lang="ts">
  import { onMount } from "svelte";

  function sel(selector: string): HTMLElement | null {
    return document.querySelector(selector);
  }

  const api_url = import.meta.env.VITE_API_URL;

  const createRoom = async (alias: string) => {
    try {
      const response = await fetch(`${api_url}/api/create-room`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ alias }),
      });
      const data = await response.json();
      const room_data = data.message;
      const cred = data.hostCredential;
      console.log(room_data);

      // Redirect to room page
      window.location.href = `/room/${room_data.id}?alias=${room_data.host}&type=host&cred=${cred}`;
    } catch (error) {
      console.error("Error creating room:", error);
    }
  };
</script>

<input type="text" id="alias" placeholder="Enter your alias" />
<button on:click={() => createRoom((sel("#alias") as HTMLInputElement).value)}
  >Create Room</button
>
