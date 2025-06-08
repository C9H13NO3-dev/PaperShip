# PaperShip

Displaying AIS position and ship info on a 10" Inkplate.

## Firmware
The `firmware/InkplateDisplay` folder contains an Arduino sketch for the
Inkplate10. It connects to WiFi, downloads a PNG image from a configured URL
once every hour and displays it on the screen in portrait mode. Replace the WiFi
credentials and `imageUrl` in `InkplateDisplay.ino` with your own values. Open
the folder in the Arduino IDE and upload to the board.

## Tracker Container
The `tracker` folder contains a small Docker setup that listens to
[AISstream.io](https://aisstream.io/documentation#Python) for messages about a
single ship (selected via the `MMSI` environment variable). It renders a
black‑and‑white summary image containing the ship name, a user supplied PNG,
current position/course/speed and a map with the ship's position marked.

Build and run the container:

```bash
docker build -t ship-tracker tracker
MMSI=123456789 AISTREAM_TOKEN=your_token \
  docker run -e MMSI -e AISTREAM_TOKEN -v $(pwd)/ship.png:/app/ship.png ship-tracker
```

The rendered image is written to `output.png` in the container's working
directory.
