import snowboydecoder
import sys
import signal
import io
import json
import click
import google.oauth2.credentials

CREDENTIAL_FILE = click.get_app_dir('google-oauthlib-tool') + "/credentials.json"

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

"""
Authenticate this device by searching default json location
"""
def gAssisantAuth():
	try:
		with io.open(CREDENTIAL_FILE, 'r') as f:
			# Validate credential
			credential = google.oauth2.credentials.Credentials(token=None, 
																**json.load(f))

			# Get an HTTP request function to refresh credentials.
			http_request = google.auth.transport.requests.Request()

			# Refresh the credential, don't know why but won't hurt
			credential.refresh()
			print("Credential Verified")
	except Exception as e:
		print("Something is wrong with the credential. ", e)
		sys.exit(-1)

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

gAssisantAuth()

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# The obj contains the hotword detection
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=snowboydecoder.play_audio_file,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
