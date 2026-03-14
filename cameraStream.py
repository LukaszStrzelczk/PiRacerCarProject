import subprocess

class CameraStreamer:

	def __init__(self, target_ip, target_port=5000):
		self.target_ip = target_ip
		self.target_port = target_port
		self.process = None
		self.on = True

	def update(self):
		cmd = [
			'ffmpeg',
			'-f', 'v4l2',
			'-input_format', 'mjpeg',
			'-video_size', '1280x720',
			'-framerate', '30',
			'-i', '/dev/video0',
            		'-c:v', 'copy',
            		'-flush_packets', '0',
            		'-max_delay', '200000',
            		'-buffer_size', '2000000',
            		'-f', 'rtp',
            		f'rtp://{self.target_ip}:{self.target_port}'
		]

		self.process = subprocess.Popen(
			cmd,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)

		self.process.wait()

	def run_threaded(self):
		"""No output needed, just keeps the stream running."""
		pass

	def shutdown(self):
		self.on = False
		if self.process:
			self.process.terminate()
			self.process.wait()
