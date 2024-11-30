let ws: WebSocket | null = null;

export const connect = () => {
    console.log("Attempting to connect...");
    return new Promise<void>((resolve, reject) => {
        if (typeof WebSocket !== "undefined") {
            console.log("WebSocket is supported.");
            ws = new WebSocket("ws://localhost:8000/ws");
        } else {
            console.error("WebSocket is not supported in this environment.");
            reject("WebSocket is not supported in this environment.");
            return;
        }

        ws.onopen = () => {
            console.log("WebSocket connection opened");
            resolve();
        };

        ws.onmessage = (event) => {
            console.log("Message from server:", event.data);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            reject(error);
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };
    });
};

export const sendMessage = (data: {event: string, message: string}) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(
        JSON.stringify({
            event: data.event,
            message: data.message,
        })
    );
  }
  else {
    console.error("WebSocket is not open");
  }
};

export const disconnect = () => {
    ws && ws.close();
};

export const onMessage = (callback: (message: string) => void) => {
    if (!ws) {
        return;
    }
    ws.onmessage = (event) => {
        callback(event.data);
    };
}

export const awaitMessage = () => {
    return new Promise<string>((resolve) => {
        if (!ws) {
            return Promise.reject("WebSocket is not connected");
        }
        ws.onmessage = (event) => {
            resolve(JSON.parse(event.data));
        };
    });
}
