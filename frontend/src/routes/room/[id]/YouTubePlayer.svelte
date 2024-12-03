<script lang="ts">
  import exp from "constants";
  import type internal from "stream";
  import { onMount } from "svelte";

  let {
    onpause = $bindable((p: YT.Player) => {
      console.error("onpause function not bound");
    }),
    onseek = $bindable((p: YT.Player) => {
      console.error("onseek function not bound");
    }),
    videoId = $bindable("dQw4w9WgXcQ"),
  } = $props();

  let player: YT.Player | null = null;

  let isPlaying: boolean = $state(false);
  let currentTime: number = $state(0);
  let duration: number = $state(0);

  let playerControls: HTMLElement;

  // Load YouTube IFrame API
  async function loadYouTubeAPI(): Promise<typeof YT> {
    return new Promise((resolve, reject) => {
      if (window.YT && window.YT.Player) {
        resolve(window.YT);
      } else {
        const tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        tag.async = true;
        tag.onload = () => {
          window.onYouTubeIframeAPIReady = () => resolve(window.YT);
        };
        tag.onerror = reject;
        document.body.appendChild(tag);
      }
    });
  }

  export function setPauseState(state: boolean) {
    isPlaying = state;
  }

  export function setControlsVisibility(state: boolean) {
    if (playerControls) {
      playerControls.style.display = state ? "flex" : "none";
    }
  }
  export function handleVideoData(video_data: {
    id: string;
    timestamp: number;
    is_paused: boolean;
  }) {
    if (player) {
      if (video_data.id !== videoId) {
        videoId = video_data.id;
        player.loadVideoById(videoId, video_data.timestamp);
      } else {
        player.seekTo(video_data.timestamp, true);
      }
      if (video_data.is_paused) {
        player.pauseVideo();
      } else {
        player.playVideo();
      }
    }
  }

  export function getVideoData() {
    return {
      id: videoId,
      timestamp: player?.getCurrentTime() || 0,
      is_paused: player?.getPlayerState() === YT.PlayerState.PAUSED,
    };
  }

  export function togglePlayPause() {
    if (player) {
      if (isPlaying) {
        player.pauseVideo();
      } else {
        player.playVideo();
      }
    }
    onpause(player);
  }

  export function handleSeek(seekTo: number) {
    if (player) {
      player.seekTo(seekTo, true);
    }
    onseek(player);
  }

  onMount(() => {
    loadYouTubeAPI()
      .then((YT) => {
        player = new YT.Player("player", {
          videoId,
          height: "390",
          width: "640",
          events: {
            onReady: (event: YT.PlayerEvent) => {
              console.log("Player is ready", event);
              duration = player?.getDuration() || 0;
            },
            onStateChange: (event: YT.OnStateChangeEvent) => {
              console.log("State changed", event);
              isPlaying = event.data === YT.PlayerState.PLAYING;
            },
          },
        });

        // Update current time every second
        const interval = setInterval(() => {
          if (player && isPlaying) {
            currentTime = player.getCurrentTime();
          }
        }, 1000);

        return () => {
          clearInterval(interval);
          player?.destroy();
        };
      })
      .catch((error) => {
        console.error("Error loading YouTube API:", error);
      });
  });
</script>

<div id="player"></div>

<div bind:this={playerControls} class="controls">
  <button onclick={togglePlayPause}>
    {isPlaying ? "Pause" : "Play"}
  </button>
  <input
    type="range"
    min="0"
    max={duration}
    step="1"
    value={currentTime}
    oninput={(event) =>
      handleSeek(Number((event.target as HTMLInputElement).value))}
  />
  <div>
    {Math.floor(currentTime / 60)}:{Math.floor(currentTime % 60)
      .toString()
      .padStart(2, "0")} /
    {Math.floor(duration / 60)}:{Math.floor(duration % 60)
      .toString()
      .padStart(2, "0")}
  </div>
</div>

<style>
  #player {
    margin: auto;
  }
  .controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 10px;
  }
  .controls button {
    margin-bottom: 10px;
  }
  .controls input[type="range"] {
    width: 100%;
    max-width: 640px;
  }
</style>
