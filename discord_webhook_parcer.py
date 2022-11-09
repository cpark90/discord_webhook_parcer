import argparse, json, threading, logging

from flask import Flask, request

from discord_webhook import DiscordWebhook, DiscordEmbed

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordWrapper:
    def __init__(self, discord_webhook_url=None):
        self.discord_webhook_url = discord_webhook_url
    
    def setDiscordWebhookURL(self, discord_webhook_url):
        self.discord_webhook_url = discord_webhook_url

    def sendWebhook(self, content):
        content_dict = json.loads(json.loads(content)["payload_json"])
        webhook = DiscordWebhook(url=self.discord_webhook_url, avatar_url=content_dict["avatar_url"])

        embed_contents = content_dict["embeds"]
        for embed_content in embed_contents:
            embed = DiscordEmbed(**embed_content)
            webhook.add_embed(embed)
        response = webhook.execute()

dw = DiscordWrapper()


app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        content = request.args.to_dict()
    elif request.method == 'POST':
        if request.is_json is True:  # Content-Type: json
            content = request.get_json()
        else:  # Content-Type: x-www-form-urlencoded
            content = json.dumps(request.form.to_dict())
    #send_discord_webhook function is on thread
    thread = threading.Thread(target=dw.sendWebhook, kwargs={'content': content})
    thread.start()
    return 'success'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",
                        default='0.0.0.0',
                        help="parcer hosting ip",
                        type=str)
    parser.add_argument("--port",
                        default=80,
                        help="parcer hosting port",
                        type=int)
    parser.add_argument("--do_debug",
                        action='store_true',
                        help="debug mode")
    parser.add_argument("--webhook_url",
                        default=None,
                        help="discord webhook url",
                        type=str)

    args = parser.parse_args()

    dw.setDiscordWebhookURL(args.webhook_url)

    app.run(host=args.host, port=args.port, debug=args.do_debug)
