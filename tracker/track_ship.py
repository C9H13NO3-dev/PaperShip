import json
import os
import sys
import requests
import websocket
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Configuration
MMSI = os.environ.get("MMSI")
TOKEN = os.environ.get("AISTREAM_TOKEN")
SHIP_IMAGE = os.environ.get("SHIP_IMAGE", "ship.png")
OUTPUT_IMAGE = os.environ.get("OUTPUT_IMAGE", "output.png")

MAP_PROVIDER = "https://static-maps.yandex.ru/1.x/?lang=en-US&l=map&ll={lon},{lat}&z=12&size=450,450"

def fetch_map(lat, lon):
    url = MAP_PROVIDER.format(lat=lat, lon=lon)
    resp = requests.get(url)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content)).convert("L")
    return img

def draw_output(name, lat, lon, course, speed):
    base_img = Image.new("L", (600, 800), 255)
    draw = ImageDraw.Draw(base_img)
    font = ImageFont.load_default()

    # Ship name
    draw.text((10, 10), name, font=font, fill=0)

    # Ship graphic
    if os.path.exists(SHIP_IMAGE):
        ship_pic = Image.open(SHIP_IMAGE).convert("L")
        ship_pic.thumbnail((200, 200))
        base_img.paste(ship_pic, (10, 40))

    # Info line
    info = f"Lat: {lat:.5f}  Lon: {lon:.5f}  COG: {course}  SOG: {speed}kt"
    draw.text((10, 260), info, font=font, fill=0)

    # Map with position
    try:
        map_img = fetch_map(lat, lon)
        map_img.thumbnail((450, 450))
        base_img.paste(map_img, (10, 300))
        px = int(10 + map_img.width / 2)
        py = int(300 + map_img.height / 2)
        draw.ellipse((px-4, py-4, px+4, py+4), fill=0)
    except Exception as e:
        print(f"Failed to fetch map: {e}")

    base_img.save(OUTPUT_IMAGE)
    print(f"Image saved to {OUTPUT_IMAGE}")


def on_message(ws, message):
    data = json.loads(message)
    for msg in data.get("messages", []):
        if str(msg.get("mmsi")) == MMSI:
            name = msg.get("shipname", "Unknown")
            lat = msg.get("lat")
            lon = msg.get("lon")
            course = msg.get("course")
            speed = msg.get("speed")
            draw_output(name, lat, lon, course, speed)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    auth = json.dumps({"APIKey": TOKEN})
    ws.send(auth)
    ws.send(json.dumps({"BoundingBoxes": [{"name": "box", "bounds": [-90,-180,90,180]}]}))


def main():
    if not MMSI or not TOKEN:
        print("MMSI and AISTREAM_TOKEN environment variables required")
        sys.exit(1)

    ws = websocket.WebSocketApp(
        "wss://stream.aisstream.io/v0/stream",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()


if __name__ == "__main__":
    main()

