import subprocess

class CameraStreamer:

	def __init__(self, target_ip, target_port=5000):
		self.target_ip = target_ip
		self.target_port = target_port
		self.process = None
		self.rpicam_process = None
		self.on = True

	def update(self):
		self.rpicam_process = subprocess.Popen(
			[
				'rpicam-vid',
				'--width', '640',
				'--height', '480',
				'--framerate', '30',
				'--codec', 'mjpeg',
				'-t', '0',
				'-o', '-'
			],
			stdout=subprocess.PIPE,
			stderr=subprocess.DEVNULL
		)

		self.process = subprocess.Popen(
			[
				'ffmpeg',
				'-f', 'mjpeg',
				'-i', '-',
				'-c:v', 'copy',
				'-flush_packets', '0',
				'-max_delay', '200000',
				'-buffer_size', '2000000',
				'-f', 'rtp',
				f'rtp://{self.target_ip}:{self.target_port}'
			],
			stdin=self.rpicam_process.stdout,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)

		self.process.wait()

	def run_threaded(self):
		pass

	def shutdown(self):
		self.on = False
		if self.process:
			self.process.terminate()
			self.process.wait()
		if self.rpicam_process:
			self.rpicam_process.terminate()
			self.rpicam_process.wait()