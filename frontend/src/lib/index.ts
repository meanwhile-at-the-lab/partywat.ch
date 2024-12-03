// place files you want to import through the `$lib` alias in this folder.
function loadYouTubeAPI() {
    return new Promise((resolve, reject) => {
      if (window.YT && window.YT.Player) {
        resolve(window.YT);
      } else {
        const tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        tag.async = true;
        tag.onload = () => {
          window.onYouTubeIframeAPIReady = () => resolve(window.YT);
        };
        tag.onerror = reject;
        document.body.appendChild(tag);
      }
    });
  }
  