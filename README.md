# PiRacerCarProject

A DonkeyCar-based autonomous RC car project for Raspberry Pi 4, using WebSocket control and RTP camera streaming. Built on the Waveshare DonkeyCar platform with PCA9685 servo/ESC control, OLED status display, and a custom desktop driver application.

## Hardware

- Raspberry Pi 4 (running Raspberry Pi OS Trixie or Bookworm)
- Waveshare DonkeyCar chassis with servo steering and ESC throttle
- PCA9685 PWM driver board (I2C address 0x40)
- SSD1306 128x32 OLED display (I2C)
- USB or CSI camera (MJPEG capable)
- Optional: INA219 power monitor, ADS1115 ADC

## Additional Dependencies

Assumes Python 3.11 venv and DonkeyCar are already set up per the separate setup guide.

### Linux Packages

```bash
sudo apt install -y ffmpeg
```

### Python Packages

```bash
pip install docopt websockets
```

## Usage

### Calibrate Steering and Throttle

```bash
cd ~/PiRacerCarProject
python calibrate.py drive
```

Then open a browser and go to `http://<pi-hostname>.local:8887/calibrate`.

### Drive with WebSocket Controller

```bash
python car.py --stream-ip <desktop-ip>
```

This starts the WebSocket server (default port 8765) for steering/throttle input and streams camera via RTP to the specified desktop IP (port 5000).



## Configuration

All car settings are in `config.py`. Override any value in `myconfig.py` (uncomment the relevant lines). Key settings:

- `STEERING_CHANNEL` / `THROTTLE_CHANNEL` — PCA9685 PWM channels
- `STEERING_LEFT_PWM` / `STEERING_RIGHT_PWM` — steering pulse range
- `THROTTLE_FORWARD_PWM` / `THROTTLE_STOPPED_PWM` / `THROTTLE_REVERSE_PWM` — throttle pulse range
- `WEBSOCKET_HOST` / `WEBSOCKET_PORT` — WebSocket server bind address
- `CAMERA_STREAM_PORT` — RTP camera stream port
- `PCA9685_I2C_ADDR` — I2C address of the PWM board

## Project Structure

```
PiRacerCarProject/
├── car.py                  # Main drive script (WebSocket + camera stream)
├── calibrate.py            # Steering/throttle calibration via web UI
├── train.py                # Model training script
├── config.py               # Default car configuration
├── myconfig.py             # User overrides (uncomment as needed)
├── webSocketController.py  # WebSocket server for remote control
├── cameraStream.py         # RTP camera streamer using ffmpeg
├── data/                   # Training data (tubs)
└── models/                 # Trained models
```
