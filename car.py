import donkeycar as dk
from donkeycar.parts.actuator import PCA9685,PWMSteering, PWMThrottle
import argparse

from webSocketController import  WebSocketController
from cameraStream import CameraStreamer

def drive(cfg, stream_ip):
	v = dk.vehicle.Vehicle()

	cam = CameraStreamer(target_ip=stream_ip, target_port=cfg.CAMERA_STREAM_PORT)
	v.add(cam, threaded=True)

	ws_controller = WebSocketController(
		host=cfg.WEBSOCKET_HOST,
		port=cfg.WEBSOCKET_PORT,
		command_timeout=getattr(cfg, 'WEBSOCKET_COMMAND_TIMEOUT', 0.5)
	)
	v.add(
		ws_controller,
		outputs=['steering', 'throttle'],
		threaded=True
	)

	steering_controller = PCA9685(
		channel=cfg.STEERING_CHANNEL,
		address=cfg.PCA9685_I2C_ADDR,
		busnum=1
	)
	steering = PWMSteering(
		controller=steering_controller,
		left_pulse=cfg.STEERING_LEFT_PWM,
		right_pulse=cfg.STEERING_RIGHT_PWM
	)

	v.add(
		steering,
		inputs=['steering']
	)

	throttle_controller = PCA9685(
		channel=cfg.THROTTLE_CHANNEL,
		address=cfg.PCA9685_I2C_ADDR,
		busnum=1
	)
	throttle = PWMThrottle(
		controller=throttle_controller,
		max_pulse=cfg.THROTTLE_FORWARD_PWM,
		min_pulse=cfg.THROTTLE_REVERSE_PWM,
		zero_pulse=cfg.THROTTLE_STOPPED_PWM
	)

	v.add(
		throttle,
		inputs=['throttle']
	)

	v.start(rate_hz=20, max_loop_count=None)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='PiRacer WebSocket Controller')
	parser.add_argument(
		'--stream-ip',
		type=str,
		default=None,
		help='IP address of desktop running Driver app'
	)
	args = parser.parse_args()

	cfg = dk.load_config()
	drive(cfg, args.stream_ip)
