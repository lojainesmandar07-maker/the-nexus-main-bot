import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from core.bot import StoryBot
from core.config import DISCORD_TOKEN


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def _start_health_server(port: int) -> None:
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    print(f"Health server listening on 0.0.0.0:{port}")
    server.serve_forever()


def main() -> None:
    # Render Web Services require a bound port; Render Workers do not.
    # Start health server only when a PORT is explicitly provided.
    port_value = os.getenv("PORT")
    if port_value:
        port = int(port_value)
        server_thread = threading.Thread(target=_start_health_server, args=(port,), daemon=True)
        server_thread.start()

    bot = StoryBot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
