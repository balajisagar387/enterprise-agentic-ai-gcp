import urllib.parse

# Replace YOUR_CLIENT_ID with the Client ID of the OAuth web application client you created
CLIENT_ID = "YOUR_CLIENT_ID"

REDIRECT_URI = "https://vertexaisearch.cloud.google.com/static/oauth/oauth.html"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPES = "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"

params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "include_granted_scopes": "true",
    "response_type": "code",
    "access_type": "offline",
    "prompt": "consent",
    "scope": SCOPES
}

auth_url = f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"

print("\n================ Constructed Authorization URI ================")
print(auth_url)
print("===============================================================\n")
