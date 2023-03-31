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
#api_endpoint = "https://api.openai.com/v1/completions"
#model = "code-davinci-002"

# Define the request headers
headers = {
	"Content-Type": "application/json",
	"Authorization": "Bearer " + api_key
}

class FallbackChatgpt(FallbackSkill):
	_conversation_history = []
	_max_history = 18

	def __init__(self):
		FallbackSkill.__init__(self)

	def initialize(self):
		self.register_fallback(self.handle_fallback_ChatGPT, 50)

	def handle_fallback_ChatGPT(self, message):
		self.log.info("Using ChatGPT fallback")
		try:
			self._conversation_history.append({"role": "user", "content": message.data['utterance']})
			payload = {
				"model": model,
				"messages": self._conversation_history
#				"max_tokens": 4096,
#				"temperature": 1,
#				"top_p": 1,
#				"frequency_penalty": 0,
#				"presence_penalty": 0
			}
			response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload))
#			self.log.error(json.dumps(response.json()))
			response_json = response.json()
			freason = response_json["choices"][0]["finish_reason"]
#			self.log.info(freason)
			response = response_json["choices"][0]["message"]["content"]
			self.speak(response)
			self._conversation_history.append({"role": "assistant", "content": response})
			if len(self._conversation_history) > self._max_history:
				self._conversation_history.pop(0)
				self._conversation_history.pop(0)
			return True
		except Exception as e:
			self.log.error("error in ChatGPT fallback request " + str(e))
			return False

# !text-davinci-003!
#	def handle_fallback_ChatGPT(self, message):
#		try:
#			payload = {
#				"model": model,
#				"prompt": message.data['utterance'],
#				"max_tokens": 2048,
#				"temperature": 0.4,
#				"top_p": 1,
#				"frequency_penalty": 0,
#				"presence_penalty": 0
#			}
#			response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload))
#			response_json = response.json()
#			freason = response_json["choices"][0]["finish_reason"]
#			self.log.info(freason)
#			response = response_json["choices"][0]["text"]
#			self.speak(response)
#			return True
#		except Exception as e:
#			self.log.error("error in ChatGPT fallback request " + str(e))
#			return False

def create_skill():
	return FallbackChatgpt()
