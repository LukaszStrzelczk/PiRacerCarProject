import asyncio
import json
import websockets

class WebSocketController:

	def __init__(self,host='0.0.0.0', port=8700):
		self.host = host
		self.port = port
		self.throttle = 0.0
		self.steering_angle = 0.0
		self.on = True

	def update(self):
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		start_server = websockets.serve(self._handler, self.host, self.port)
		loop.run_until_complete(start_server)
		loop.run_forever()

	async def _handler(self, websocket, path):
		async for message in websocket:
			if not self.on:
				break
			try:
				data = json.loads(message)
				self.throttle = float(data.get('throttle', 0.0))
				self.steering_angle = float(data.get('steering', 0.0))
			except (json.JSONDecodeError, ValueError) as e:
				print(f"Invalid message: {e}")

	def run_threaded(self):
		return self.steering_angle, self.throttle

	def shutdown(self):
		self.on = False
