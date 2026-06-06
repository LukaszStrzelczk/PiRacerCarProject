import asyncio
import json
import time
from threading import Lock

import websockets

class WebSocketController:

	def __init__(self, host='0.0.0.0', port=8700, command_timeout=0.5):
		self.host = host
		self.port = port
		self.command_timeout = command_timeout
		self.throttle = 0.0
		self.steering_angle = 0.0
		self.connected = False
		self.last_message_at = 0.0
		self.on = True
		self._lock = Lock()

	def update(self):
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)

		async def main():
			async with websockets.serve(self._handler, self.host, self.port):
				await asyncio.Future()  

		loop.run_until_complete(main())

	async def _handler(self, websocket):
		self._mark_connected()
		try:
			async for message in websocket:
				if not self.on:
					break
				try:
					data = json.loads(message)
					steering_angle, throttle = self._parse_command(data)
					self._set_controls(steering_angle, throttle)
				except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as e:
					print(f"Invalid message: {e}")
					self._stop_for_safety()
		finally:
			self._mark_disconnected()

	def _parse_command(self, data):
		if not isinstance(data, dict):
			raise ValueError('control message must be a JSON object')

		steering_angle = self._clamp(float(data.get('steering', 0.0)))
		throttle = self._clamp(float(data.get('throttle', 0.0)))

		if self._reverse_requested(data):
			throttle = -abs(throttle)

		return steering_angle, throttle

	def _reverse_requested(self, data):
		for key in ('reverse', 'is_reverse', 'isReverse'):
			if key in data:
				return self._truthy(data[key])

		direction = str(data.get('direction', data.get('gear', ''))).strip().lower()
		return direction in ('reverse', 'backward', 'backwards', 'back')

	def _truthy(self, value):
		if isinstance(value, bool):
			return value
		if isinstance(value, (int, float)):
			return value != 0
		if isinstance(value, str):
			return value.strip().lower() in ('1', 'true', 'yes', 'y', 'on', 'reverse')
		return False

	def _clamp(self, value):
		return max(-1.0, min(1.0, value))

	def _mark_connected(self):
		with self._lock:
			self.connected = True
			self.last_message_at = time.monotonic()

	def _mark_disconnected(self):
		with self._lock:
			self.connected = False
			self.steering_angle = 0.0
			self.throttle = 0.0

	def _set_controls(self, steering_angle, throttle):
		with self._lock:
			self.steering_angle = steering_angle
			self.throttle = throttle
			self.last_message_at = time.monotonic()

	def _stop_for_safety(self):
		with self._lock:
			self.steering_angle = 0.0
			self.throttle = 0.0

	def run_threaded(self):
		with self._lock:
			if self._connection_lost():
				self.steering_angle = 0.0
				self.throttle = 0.0
			return self.steering_angle, self.throttle

	def _connection_lost(self):
		if not self.connected:
			return True
		if not self.command_timeout:
			return False
		return time.monotonic() - self.last_message_at > self.command_timeout

	def shutdown(self):
		self.on = False
		self._stop_for_safety()
