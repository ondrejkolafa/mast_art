from bs4 import BeautifulSoup
from mastodon import Mastodon
from openai import OpenAI
import requests
import os

HASHTAG = "Ukraine"

mastodon = Mastodon(
    client_id=os.environ["MAST_CLIENT_ID"], client_secret=os.environ["MAST_CLIENT_SECRET"], api_base_url="https://mastodon.social"
)

token = mastodon.log_in(os.environ["MAST_USERNAME"], os.environ["MAST_PASSWORD"])

print(f"Logged in as {mastodon.account_verify_credentials()['acct']}")

toots = mastodon.timeline_hashtag(HASHTAG, limit=10)

print(f"Found {len(toots)} toots")

llm_input = []
i = 1

for toot in toots:
    text = BeautifulSoup(toot["content"]).get_text()
    print(f"{toot['account']['username']} in {toot['language']} : {text}")
    llm_input.append(f"{i}.\t{text}\t(language: {toot['language']})\n")
    i += 1

print(" ".join(llm_input))


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("MAST_OPENAI_TOKEN"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are summary robot. Try to get the most important information and sum it up. We are not interested in personal incidents, unless the person i considered VIP and it might affect the whole war. It must be at maximum 500 characters.",
        },
        {"role": "user", "content": llm_input},
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion)

# # Check if the request was successful
# if response.status_code == 200:
#     print("Response from OpenAI:", response.json())
#     print("\n")
#     print(response.json()["choices"][0]["message"]["content"])
# else:
#     print("Error:", response.status_code, response.text)
