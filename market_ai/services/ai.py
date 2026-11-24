
import os
import streamlit as st


def _secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def _client():
    """Connect to Groq first, then OpenAI if Groq is unavailable."""

    try:
        from openai import OpenAI

        groq_key = _secret("GROQ_API_KEY")

        if groq_key:
            client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )
            model = _secret(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            )
            return client, model

        openai_key = _secret("OPENAI_API_KEY")

        if openai_key and openai_key != "your-key":
            client = OpenAI(api_key=openai_key)
            return client, "gpt-4.1-mini"

    except Exception:
        return None, None

    return None, None


def _ask_ai(messages, max_tokens=1600):
    client, model = _client()

    if not client:
        return None

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


def generate_marketing_copy(
    category,
    business,
    offer,
    audience,
    details,
    tone,
    length,
    uploaded=None
):
    prompt = f"""
You are Market AI, a professional advertising strategist.

Create a practical advertising campaign for:

Category: {category}
Business: {business or 'Not supplied'}
Offer: {offer}
Target audience: {audience or 'General relevant audience'}
Verified details: {details or 'None supplied'}
Tone: {tone}
Target length: {length}

Return:
1. Campaign concept
2. Attention-grabbing opening hook
3. Advertising script and voice-over
4. Scene-by-scene storyboard
5. On-screen text
6. Social media caption
7. Call to action
8. Factual accuracy checklist

Never invent prices, dates, addresses, phone numbers,
product claims or event details.
Clearly identify missing information.
"""

    try:
        result = _ask_ai([
            {
                "role": "system",
                "content": "You are Market AI's expert advertising strategist."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])

        if result:
            return result

    except Exception as e:
        return f"AI service error: {e}"

    return _fallback(category, business, offer, details, length) + (
        "\n\nDemo mode: Configure GROQ_API_KEY in Streamlit Secrets."
    )


def _fallback(category, business, offer, details, length):
    return f"""
### Campaign concept

A clear, benefit-led {category.lower()} campaign
for **{business or 'your business'}**.

### Hook

"Looking for {offer.lower()}? Discover an option worth knowing about."

### Suggested voice-over

"Discover {offer}. Explore the details, see what makes
it right for you, and get in touch today."

### Storyboard

1. Opening: An attention-grabbing introduction.
2. Showcase: Present the product, service or event.
3. Key information: {details or 'Add verified details.'}
4. Call to action: Invite viewers to get in touch.

### Social caption

Discover {offer}. Send us a message to learn more.

### Accuracy checklist

- Confirm price and availability.
- Verify contact information.
- Do not publish unverified claims.
"""


def assistant_reply(history):
    """Natural, context-aware Market AI Buddy conversation."""

    system_prompt = """
You are MARKET AI BUDDY, the intelligent conversational
assistant inside the MARKET AI platform.

YOUR PERSONALITY:
- Friendly, warm, intelligent and approachable.
- Speak naturally, like a helpful conversational AI companion.
- Be professional without sounding robotic.
- Be conversational, not like a customer-service script.
- Adapt your tone to the user's mood and communication style.

HOW TO START CONVERSATIONS:
- If someone says "Hey buddy", greet them warmly.
- Ask how they are doing.
- If they ask how you are, respond naturally and warmly.
- Do not immediately start selling Market AI services.
- Do not force every conversation into business or marketing.

CONVERSATION INTELLIGENCE:
- Understand the full conversation, not just the latest message.
- Remember the context provided in the conversation history.
- Answer follow-up questions naturally.
- Ask relevant questions when clarification is needed.
- Avoid repeating greetings unnecessarily.
- Give useful, clear and thoughtful answers.

YOUR KNOWLEDGE AND ABILITIES:
- General conversations and everyday questions.
- Business development and entrepreneurship.
- Marketing and advertising strategies.
- Promotional messages, speeches and proposals.
- Customer acquisition and business growth.
- Product, event, beauty and service advertising.
- Creative ideas, storytelling and content planning.
- Helping users understand how to use MARKET AI.

IMPORTANT:
- You are not restricted to business conversations.
- Never pretend to have performed an action you did not perform.
- Never invent facts, statistics or current news.
- Do not claim to publish adverts or connect accounts unless
  the application actually provides that capability.
- Give practical answers rather than generic motivational replies.

Remember: You are a genuine conversational AI assistant,
not a fixed-response chatbot.
"""

    if not history:
        return "Hey buddy! How are you doing today?"

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for item in history[-20:]:
        role = item.get("role")
        content = item.get("content", "")

        if role in ("user", "assistant") and content:
            messages.append({
                "role": role,
                "content": str(content)
            })

    try:
        result = _ask_ai(messages, max_tokens=1800)

        if result:
            return result

        return (
            "Hey buddy! I'm here, but my AI connection isn't "
            "configured yet. Please check the GROQ_API_KEY "
            "in Streamlit Secrets."
        )

    except Exception as e:
        return (
            "I'm having trouble connecting to my AI service. "
            "Please check the Groq API configuration. "
            f"Technical detail: {e}"
        )
