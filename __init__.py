from mycroft import FallbackSkill, intent_handler
import requests
import urllib
import json
import os


def read_config() -> dict:
	filename = os.path.join(os.path.dirname(__file__), 'config.json')
	try:
		with open(filename, mode='r') as f:
			return json.loads(f.read())
	except FileNotFoundError:
		return {}

confs = read_config()

api_endpoint = confs["API_ENDPOINT"]
api_key = confs["API_KEY"]
model = confs["MODEL"]
#api_endpoint = "https://api.openai.com/v1/chat/completions"
#model = "text-davinci-003"

# Define the request headers
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer " + api_key
}

class FallbackChatgpt(FallbackSkill):
	def __init__(self):
		FallbackSkill.__init__(self)

	def initialize(self):
		self.register_fallback(self.handle_fallback_ChatGPT, 8)

	def handle_fallback_ChatGPT(self, message):
		try:
			payload = {
				"model": model,
				"prompt": message.data['utterance'],
				"max_tokens": 2048,
				"temperature": 0.4,
				"top_p": 1,
				"frequency_penalty": 0,
				"presence_penalty": 0
			}
			response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload))
			response_json = response.json()
			freason = response_json["choices"][0]["finish_reason"]
			self.log.info(freason)
			response = response_json["choices"][0]["text"]
			self.speak(response)
			return True
		except:
			self.log.info("error in ChatGPT fallback request")
			return False

def create_skill():
	return FallbackChatgpt()
