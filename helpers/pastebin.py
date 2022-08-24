import requests
from helpers.config import PASTEBIN_TOKEN
 
# Function to post to pastebin
def paste(text : str, title : str):
	url = "https://pastebin.com/api/api_post.php"
	payload = {
		"api_dev_key": PASTEBIN_TOKEN,
		"api_option": "paste",
		"api_paste_code": text,
		"api_paste_name": title,
		"api_paste_private": "1",
		"api_paste_expire_date": "N",
		"api_paste_format": "python"
	}
	r = requests.post(url, data = payload)

	if r.status_code == 200:
		return r.text
	
	else:
		return "Error"