import os, requests, streamlit as st

BASE = "https://api.replicate.com/v1"

def _secret(name, default=""):
    try: return st.secrets.get(name, os.getenv(name, default))
    except Exception: return os.getenv(name, default)

def generate_video(model, prompt, image_file=None, duration="5 seconds"):
    token = _secret("REPLICATE_API_TOKEN")
    if not token:
        return {"error":"REPLICATE_API_TOKEN is not configured. Add a provider token and ensure the account has available credits. Video generation cannot run without it."}
    # Replicate model prediction API. Model input fields differ by model; this adapter uses
    # common prompt/image/duration fields and reports provider validation errors transparently.
    payload = {"input":{"prompt":prompt, "duration":int(duration.split()[0])}}
    if image_file is not None:
        return {"error":"Image-to-video requires uploading the image to durable storage and passing a provider-accessible URL. This first adapter currently supports text-to-video; image reference support is planned for the next integration step."}
    url = f"{BASE}/models/{model}/predictions"
    try:
        response = requests.post(url, json=payload, headers={
            "Authorization":f"Bearer {token}",
            "Content-Type":"application/json",
            "Prefer":"wait"
        }, timeout=90)
        if response.status_code not in (200,201):
            return {"error":f"Video provider rejected the request ({response.status_code}): {response.text[:1200]}"}
        data = response.json()
        return {"id":data.get("id"),"status":data.get("status"),"video_url":_extract_url(data.get("output"))}
    except requests.RequestException as e:
        return {"error":f"Could not contact the video provider: {e}"}

def _extract_url(output):
    if isinstance(output,str) and output.startswith("http"): return output
    if isinstance(output,list):
        for item in output:
            if isinstance(item,str) and item.startswith("http"): return item
    if isinstance(output,dict):
        for value in output.values():
            if isinstance(value,str) and value.startswith("http"): return value
    return None

def poll_video(prediction_id):
    token = _secret("REPLICATE_API_TOKEN")
    if not token: return {"error":"REPLICATE_API_TOKEN is not configured."}
    try:
        r = requests.get(f"{BASE}/predictions/{prediction_id}",
                         headers={"Authorization":f"Bearer {token}"}, timeout=30)
        if r.status_code != 200: return {"error":f"Provider status check failed: {r.text[:800]}"}
        data = r.json()
        return {"status":data.get("status"),"video_url":_extract_url(data.get("output")),
                "details":data.get("error")}
    except requests.RequestException as e:
        return {"error":str(e)}
