import streamlit as st
from services.db import init_db, save_business, list_businesses, save_campaign, list_campaigns
from services.ai import generate_marketing_copy, assistant_reply
from services.video import generate_video, poll_video
from services.news import get_news

st.set_page_config(page_title="MARKET AI", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
:root { --blue:#1677D2; --green:#16A36A; --navy:#10243A; }
.stApp { background: linear-gradient(145deg,#f7fbff 0%,#eef7ff 55%,#f4fff9 100%); }
[data-testid="stSidebar"] { background:#10243A; }
[data-testid="stSidebar"] * { color:#fff !important; }
.hero { padding:1.5rem 1.7rem; border-radius:22px; color:white;
background:linear-gradient(115deg,#1269bd 0%,#1688d8 48%,#16a36a 100%); }
.hero h1 { font-size:2.45rem; margin:0; letter-spacing:-1px; }
.hero p { opacity:.95; margin:.35rem 0 0 0; }
.metric-card { background:white; border:1px solid #deebf5; border-radius:16px; padding:16px; }
.small-muted { color:#5b7084; font-size:.9rem; }
div.stButton > button[kind="primary"] { background:linear-gradient(90deg,#1677D2,#16A36A); border:0; }
</style>
""", unsafe_allow_html=True)

MODULES = [
    "Dashboard", "Create Advert", "AI Video Studio", "AI Assistant",
    "Products", "Events", "Beauty", "Business Services",
    "Social Hub", "Market Live", "Campaigns", "Analytics",
    "Publicity Network", "Creator Network", "Business Profile", "Settings"
]
with st.sidebar:
    st.markdown("## 🌐 MARKET AI")
    st.caption("Every Business Deserves a Voice.")
    page = st.radio("WORKSPACE", MODULES, label_visibility="visible")
    st.divider()
    st.caption("Build small. Build properly. Design for scale.")

def header(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
    st.write("")

def metric(label, value, note):
    st.markdown(f'<div class="metric-card"><div class="small-muted">{label}</div><h2>{value}</h2><div class="small-muted">{note}</div></div>', unsafe_allow_html=True)

if page == "Dashboard":
    header("Your business deserves to be seen.", "Your AI-powered workspace for advertising, publicity and business growth.")
    businesses = list_businesses()
    campaigns = list_campaigns()
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric("Business profiles", len(businesses), "Saved in this workspace")
    with c2: metric("Campaigns", len(campaigns), "Created campaign records")
    with c3: metric("Creative studio", "Ready", "Copy and campaign planning")
    with c4: metric("Video generation", "API needed", "Connect a funded provider to render")
    st.subheader("Explore Market AI")
    cols = st.columns(3)
    cards = [
        ("🎬 Create an advert","Turn product photos, flyers and business details into campaign concepts."),
        ("✨ AI Video Studio","Submit a prompt or image to a real video-generation provider."),
        ("🧠 Market AI Assistant","Get marketing ideas, business advice and promotional writing."),
        ("📣 Social Hub","Prepare platform-specific posts and track publishing tasks."),
        ("📰 Market Live","Browse business and technology headlines from RSS sources."),
        ("🌍 Publicity Network","Prepare business listings for a future discovery marketplace.")
    ]
    for i,(title,desc) in enumerate(cards):
        with cols[i%3]:
            st.markdown(f"**{title}**")
            st.write(desc)

elif page == "Business Profile":
    header("Business Profile","Tell Market AI what you offer so it can create more relevant campaigns.")
    with st.form("business_form"):
        name = st.text_input("Business name")
        category = st.selectbox("Business category",["Products","Events","Beauty","Business services","Fashion","Food","Real estate","Other"])
        description = st.text_area("What do you sell or provide?")
        location = st.text_input("Business location")
        contact = st.text_input("Public business contact (optional)")
        submitted = st.form_submit_button("Save business profile", type="primary")
        if submitted:
            if name.strip() and description.strip():
                save_business(name, category, description, location, contact)
                st.success("Business profile saved.")
            else: st.warning("Please enter a business name and description.")
    for b in list_businesses():
        with st.expander(b["name"]):
            st.write(f'**Category:** {b["category"]}')
            st.write(b["description"])
            st.caption(f'{b["location"]} · {b["contact"]}')

elif page in ["Create Advert","Products","Events","Beauty","Business Services"]:
    section = page if page != "Create Advert" else "All categories"
    header("AI Advert Studio", f"Create advertising concepts for {section.lower()}.")
    st.info("This workflow creates campaign copy and a production brief. Image/video rendering requires the relevant connected generation provider.")
    category_options = ["Product","Event","Beauty & lifestyle","Business service","Fashion","Food & beverage","Real estate","Other"]
    category = st.selectbox("What are you advertising?", category_options,
        index=category_options.index("Product") if page=="Products" else category_options.index("Event") if page=="Events" else category_options.index("Beauty & lifestyle") if page=="Beauty" else category_options.index("Business service") if page=="Business Services" else 0)
    uploaded = st.file_uploader("Upload product image, event flyer or business image", type=["png","jpg","jpeg","webp","pdf"])
    business_name = st.text_input("Business / brand name")
    offer = st.text_input("What are you promoting?")
    audience = st.text_input("Who should this advert reach?", placeholder="e.g. working professionals in Abuja")
    key_details = st.text_area("Important details to preserve", placeholder="Price, date, venue, address, phone number, features...")
    tone = st.selectbox("Advertising style",["Professional","Luxury","Energetic","Friendly","Emotional storytelling","Minimal and modern"])
    length = st.selectbox("Campaign length",["15 seconds","30 seconds","60 seconds","Social post only"])
    if st.button("Create advertising concept", type="primary"):
        if not offer.strip():
            st.warning("Describe what you are promoting first.")
        else:
            with st.spinner("Developing your campaign..."):
                result = generate_marketing_copy(category, business_name, offer, audience, key_details, tone, length, uploaded)
            st.session_state["last_ad"] = result
            st.session_state["last_campaign_meta"] = (category,business_name,offer)
    if "last_ad" in st.session_state:
        st.subheader("Your advertising concept")
        st.markdown(st.session_state["last_ad"])
        if st.button("Save campaign"):
            meta = st.session_state.get("last_campaign_meta",("General","","Campaign"))
            save_campaign(meta[1] or "My business", meta[0], meta[2], st.session_state["last_ad"])
            st.success("Campaign saved.")

elif page == "AI Video Studio":
    header("AI Video Studio","Generate real promotional video using a connected video-generation API.")
    st.warning("Real rendering requires a provider API key, a supported model and available provider credits. This app does not pretend a text storyboard is a generated video.")
    provider = st.selectbox("Provider",["Replicate"])
    model = st.text_input("Replicate model slug", value=os.getenv("REPLICATE_MODEL",""), placeholder="owner/model-name")
    prompt = st.text_area("Describe the video", placeholder="A cinematic 15-second advert showing...")
    image = st.file_uploader("Optional reference image", type=["png","jpg","jpeg","webp"])
    duration = st.selectbox("Target duration",["5 seconds","10 seconds","15 seconds"])
    if st.button("Generate real AI video", type="primary"):
        if not model.strip() or not prompt.strip():
            st.error("Enter a supported model slug and a detailed prompt.")
        else:
            with st.spinner("Submitting video generation request..."):
                result = generate_video(model.strip(), prompt.strip(), image, duration)
            if result.get("error"): st.error(result["error"])
            else:
                st.session_state["video_prediction_id"] = result["id"]
                st.success(f'Request submitted. Job ID: {result["id"]}')
                st.caption("Keep this page open and check the job status below.")
    job_id = st.session_state.get("video_prediction_id")
    if job_id:
        st.write("**Generation status**")
        if st.button("Check video status"):
            result = poll_video(job_id)
            if result.get("error"): st.error(result["error"])
            else:
                st.write("Status:", result.get("status"))
                if result.get("video_url"):
                    st.video(result["video_url"])
                    st.markdown(f'[Open generated video]({result["video_url"]})')
                elif result.get("status") == "failed":
                    st.error(result.get("details","The provider reported a generation failure."))

elif page == "AI Assistant":
    header("Market AI Assistant","Your conversational business and marketing partner.")
    if "chat" not in st.session_state: st.session_state.chat = []
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt = st.chat_input("Ask Market AI about your business, marketing or advertising...")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = assistant_reply(st.session_state.chat)
            st.markdown(answer)
        st.session_state.chat.append({"role":"assistant","content":answer})

elif page == "Social Hub":
    header("Market Social Hub","Prepare content for your connected social channels.")
    st.info("Direct publishing requires official platform developer apps, OAuth permissions and platform-specific approval. Do not enter social media passwords here.")
    caption = st.text_area("Post or campaign copy")
    platforms = st.multiselect("Select target platforms",["Instagram","Facebook","TikTok","YouTube","LinkedIn","X"])
    if st.button("Prepare publishing checklist", type="primary"):
        if not caption.strip() or not platforms: st.warning("Add content and select at least one platform.")
        else:
            st.session_state["social_checklist"] = (caption,platforms)
            st.success("Publishing checklist prepared. No post has been published.")
    if "social_checklist" in st.session_state:
        text, selected = st.session_state["social_checklist"]
        st.write("**Content preview**"); st.write(text)
        st.write("**Selected platforms:**",", ".join(selected))
        st.caption("Connect and authorize each platform's official API before enabling live publishing.")

elif page == "Market Live":
    header("Market Live","Business, entrepreneurship, finance and technology headlines.")
    category = st.selectbox("News focus",["Business","Technology","Entrepreneurship","Finance"])
    if st.button("Refresh headlines"):
        st.session_state["news_items"] = get_news(category)
    items = st.session_state.get("news_items", get_news("Business"))
    if not items: st.info("No headlines could be retrieved. Check your internet connection or try again.")
    for item in items:
        st.markdown(f"**{item['title']}**")
        st.caption(f"{item['source']} · {item['published']}")
        st.write(item["summary"])
        st.markdown(f"[Read original]({item['link']})")
        st.divider()

elif page == "Campaigns":
    header("Campaign Manager","Your saved advertising concepts and campaign records.")
    campaigns = list_campaigns()
    if not campaigns: st.info("Your saved campaigns will appear here.")
    for c in campaigns:
        with st.expander(f'{c["business"]} — {c["offer"]}'):
            st.caption(f'{c["category"]} · {c["created_at"]}')
            st.markdown(c["content"])

elif page == "Analytics":
    header("Campaign Analytics","A single place to understand campaign activity.")
    campaigns = list_campaigns()
    st.metric("Saved campaigns",len(campaigns))
    st.info("Reach, views, clicks, leads and conversions will appear when connected advertising/social platforms provide those metrics. No performance numbers are fabricated.")

elif page == "Publicity Network":
    header("Market Publicity Network","A future-facing business discovery and promotion directory.")
    st.info("The directory foundation is being prepared. Public listings, moderation, search, verified business profiles and sponsored placements must be enabled before this becomes a public marketplace.")
    with st.form("listing_form"):
        business = st.text_input("Business name")
        category = st.selectbox("Category",["Products","Events","Beauty","Services","Food","Fashion","Other"])
        about = st.text_area("Public description")
        location = st.text_input("City / country")
        submit = st.form_submit_button("Save draft listing")
        if submit and business and about:
            save_business(business,category,about,location,"")
            st.success("Draft saved to your local business directory.")

elif page == "Creator Network":
    header("Creator Network","A foundation for future creator and publisher partnerships.")
    st.info("Creator onboarding and campaign matching can be tested as a private pilot. Payments, verified referrals, fraud prevention and attribution must be implemented before public commissions begin.")
    with st.form("creator_form"):
        name = st.text_input("Creator / publisher name")
        channel = st.text_input("Main channel or publication")
        audience = st.text_input("Audience description")
        submit = st.form_submit_button("Register interest")
        if submit and name:
            st.success("Interest recorded for this session. Persistent creator onboarding will be added with the account database.")

elif page == "Settings":
    header("Settings","Configure integrations securely.")
    st.write("Add secrets in Streamlit Community Cloud → App → Settings → Secrets. Never commit API keys to GitHub.")
    st.code('OPENAI_API_KEY = "your-key"\nREPLICATE_API_TOKEN = "your-token"\nREPLICATE_MODEL = "owner/model-name"\nSUPABASE_URL = "your-project-url"\nSUPABASE_KEY = "your-anon-key"', language="toml")
    st.caption("The initial release uses a local SQLite database. For persistent multi-user production use, connect Supabase before public launch.")
