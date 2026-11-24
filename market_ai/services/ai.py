import os
import streamlit as st

def _secret(name, default=""):
    try: return st.secrets.get(name, os.getenv(name, default))
    except Exception: return os.getenv(name, default)

def _client():
    key = _secret("OPENAI_API_KEY")
    if not key: return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=key)
    except Exception:
        return None

def generate_marketing_copy(category, business, offer, audience, details, tone, length, uploaded=None):
    client = _client()
    prompt = f"""Act as Market AI, a professional advertising strategist.
Create a practical advertising campaign for:
Category: {category}
Business: {business or 'Not supplied'}
Offer: {offer}
Target audience: {audience or 'General relevant audience'}
Details that must remain accurate: {details or 'None supplied'}
Tone: {tone}
Target length: {length}
Return: campaign concept, hook, script/voice-over, scene-by-scene storyboard, on-screen text,
social caption, call to action, and a factual accuracy checklist. Never invent prices, dates,
addresses, phone numbers, product claims or event details. Clearly mark missing details.
"""
    if client:
        try:
            response = client.responses.create(model="gpt-4.1-mini", input=prompt)
            return response.output_text
        except Exception as e:
            return f"AI service error: {e}\n\n{_fallback(category, business, offer, details, length)}"
    return _fallback(category, business, offer, details, length) + "\n\n*Demo mode: add OPENAI_API_KEY in Streamlit secrets to enable live AI generation.*"

def _fallback(category, business, offer, details, length):
    return f"""### Campaign concept
A clear, benefit-led {category.lower()} campaign for **{business or 'your business'}**.

### Hook
“Looking for {offer.lower()}? Discover an option worth knowing about.”

### Suggested voice-over
“Discover {offer}. Explore the details, see what makes it right for you, and get in touch today.”

### Storyboard
1. **Opening:** A clean, attention-grabbing introduction to the offer.
2. **Showcase:** Present the product, service or event clearly.
3. **Key information:** Display only confirmed details: {details or 'Add verified details before publishing.'}
4. **Call to action:** Invite viewers to contact the business or learn more.

### Social caption
Discover {offer}. Send us a message to learn more.

### Accuracy checklist
- Confirm price, availability and contact information.
- Do not publish unverified claims.
- Add the original flyer or product details where relevant.
"""
def assistant_reply(history):
    client = _client()
    if client:
        try:
            messages = [{"role":m["role"],"content":m["content"]} for m in history[-12:]]
            response = client.responses.create(
                model="gpt-4.1-mini",
                instructions="You are Market AI, a practical, honest business growth and marketing assistant. Ask concise clarifying questions when needed. Do not invent facts.",
                input=messages
            )
            return response.output_text
        except Exception as e:
            return f"I couldn't reach the AI service: {e}. Please check your API key and usage balance."
    last = history[-1]["content"] if history else ""
    return ("I can help plan your marketing, advertising, customer outreach and business growth. "
            "For live AI conversations, add OPENAI_API_KEY to Streamlit secrets. "
            f"\n\nYou asked: **{last}**")
