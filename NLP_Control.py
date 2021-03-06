import snowboydecoder
import sys
import signal

from GoogleAssistant import GoogleAssistant
from i2c import I2C

SLAVE_ADDR = 0x62
interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


"""
if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)
"""

def startNLP(model):
	#model = sys.argv[1]
	def detectedCallback():
		detector.terminate() # So google Assistant can use audio device
		snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING);
		assistant.startAssist()
		snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
		detector.start(detected_callback=detectedCallback,
					   interrupt_check=interrupt_callback,
		               sleep_time=0.03)

	i2c = I2C(SLAVE_ADDR)
	assistant = GoogleAssistant(i2c)

	# capture SIGINT signal, e.g., Ctrl+C
	signal.signal(signal.SIGINT, signal_handler)

	# The obj contains the hotword detection
	snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING);
	snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
	detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
	print('Listening... Press Ctrl+C to exit')

	# main loop
	detector.start(detected_callback=detectedCallback,#snowboydecoder.play_audio_file,
               	   interrupt_check=interrupt_callback,
               	   sleep_time=0.03)

	detector.terminate()
