# import requests, json

# # ====== FILL THESE ======
# ACCESS_TOKEN = "EAAYZCt6WtMloBPYdk9Pc0ftoLZAMsaQoCRCX9q69ZAZAtCi8J6BrlBGSVVoMXfNO3akijDv53ZAbETU6pZB3bsakEeqkVEaV1b6aUzZAk9S61wopUW5Nyax5f7pSTJLrmbYq4gUjUfvCXNXc6yFbnd1eeHvE96H1Bq8iWDTAiRgpH7WZAh68ZCXggf84wxlaFCu4Tq4byL8jc1t6S2ZBuCZBxAFEE9dogcCZAcXm6fEc"
# APP_ID = "1758907851420250"            # from App Settings -> Basic
# APP_SECRET = "bb2422a2ae6a21fe586ada2af7e52caf"    # from App Settings -> Basic
# # ========================

# APP_ACCESS_TOKEN = f"{APP_ID}|{APP_SECRET}"

# def call(url):
#     r = requests.get(url)
#     try:
#         return r.json()
#     except Exception:
#         return {"error": "non-json response", "text": r.text}

# print("1) Debug token (checks scopes, app_id, user_id):")
# url_debug = f"https://graph.facebook.com/debug_token?input_token={ACCESS_TOKEN}&access_token={APP_ACCESS_TOKEN}"
# debug = call(url_debug)
# print(json.dumps(debug, indent=2))

# print("\n2) /me (who the token belongs to):")
# me = call(f"https://graph.facebook.com/v17.0/me?fields=id,name&access_token={ACCESS_TOKEN}")
# print(json.dumps(me, indent=2))

# print("\n3) /me/accounts (Pages visible to this token):")
# pages = call(f"https://graph.facebook.com/v17.0/me/accounts?access_token={ACCESS_TOKEN}")
# print(json.dumps(pages, indent=2))

# # If pages is empty, show some more probes:
# if pages.get("data") == []:
#     print("\n4) Extra probes:")
#     # show app id reported by token (if present)
#     app_id = debug.get("data", {}).get("app_id")
#     print(f"- app_id in token (from debug): {app_id}")
#     # show scopes from token
#     scopes = debug.get("data", {}).get("scopes")
#     print(f"- scopes in token: {scopes}")
#     # show 'is_valid'
#     print(f"- token is_valid: {debug.get('data', {}).get('is_valid')}")
#     # try to call a known Page public info if you have PAGE_ID (optional)
#     # print("Try fetching your Page public info (replace PAGE_ID if you know it):")
#     # p = call(f"https://graph.facebook.com/v17.0/PAGE_ID?fields=id,name,about&access_token={ACCESS_TOKEN}")
#     # print(json.dumps(p, indent=2))



#url_debug = f"https://graph.instagram.com/18047432258661380?fields=media_url&access_token=EAAJP3VRQ384BPYCgZBHxjl3CGWi5R7xnNVZAbmsxsxutIcdGA1tMp2GL4Wln1AdUsjZCDqj2AOeFKvZBaHUb9mkNYZAh0j60AsiNIVVFjNFgGqBdmr0RjJFV6D6Ozw9bBZBTEdzXAJfmZBgOZBIXsp2LRcZAXzPD2v9YpsdVg9JM342RENbvs5JVWeMhSFjAchaepqeAWHOeqtFVZC73xEZCY7ZBmdDrXIw5y4uSiiDhZAqrS"