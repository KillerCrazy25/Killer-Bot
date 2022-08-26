import logging
from colorlog import ColoredFormatter

class Logger(logging.Logger):
	def __init__(self):
		super().__init__("Logger")
		self.input = 24
		logging.addLevelName(self.input, 'INPUT')
		formatter = ColoredFormatter(
			'%(log_color)s[%(name)s] %(levelname)-8s:%(reset)s %(message)s',
			log_colors={
				'DEBUG': 'cyan',
				'INFO': 'green',
				'WARNING': 'yellow',
				'ERROR': 'red',
				'CRITICAL': 'bold_red',
				'INPUT': 'blue',
			},
			datefmt='%H:%M:%S',
			reset=True
		)
		self.console_handler = logging.StreamHandler()
		self.console_handler.setFormatter(formatter)
		self.console_handler.setLevel(logging.DEBUG)
		self.addHandler(self.console_handler)
		self.setLevel(logging.INFO)
