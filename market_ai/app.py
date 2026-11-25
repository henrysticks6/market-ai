import streamlit as st
import os
from services.db import init_db, save_business, list_businesses, save_campaign, list_campaigns
from services.ai import generate_marketing_copy, assistant_reply
from services.video import generate_video, poll_video
from services.news import get_news

st.set_page_config(page_title="MARKET AI", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
:root {
    --blue: #1677D2;
    --green: #16A36A;
    --navy: #10243A;
}

/* Main application background */
.stApp {
    background: linear-gradient(
        145deg,
        var(--background-color, #f7fbff) 0%,
        #eef7ff 55%,
        #f4fff9 100%
    );
}

/* Main content width and spacing */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--navy);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Hero section */
.hero {
    padding: 1.5rem 1.7rem;
    border-radius: 22px;
    color: white !important;
    background: linear-gradient(
        115deg,
        #1269bd 0%,
        #1688d8 48%,
        #16a36a 100%
    );
}

.hero h1 {
    font-size: 2.45rem;
    margin: 0;
    letter-spacing: -1px;
    color: white !important;
}

.hero p {
    opacity: .95;
    margin: .35rem 0 0 0;
    color: white !important;
}

/* Dashboard and feature cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
}

/* Buttons */
div.stButton > button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 600;
    transition: all .2s ease;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #1677D2, #16A36A);
    border: 0;
    color: white;
}

div.stButton > button:hover {
    border-color: var(--green);
}

/* Form fields */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div {
    border-radius: 10px;
}

/* Small supporting text */
.small-muted {
    font-size: .9rem;
}

/* Mobile layout */
@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 1.2rem;
        border-radius: 16px;
    }

    .hero h1 {
        font-size: 1.7rem;
    }

    div.stButton > button {
        font-size: .85rem;
    }
}
</style>
""", unsafe_allow_html=True)

def header(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True
    )
    st.write("")

MODULES = [
    "Dashboard", "Create Advert", "AI Video Studio", "AI Assistant",
    "Products", "Events", "Beauty", "Business Services",
    "Social Hub", "Market Live", "Campaigns", "Analytics",
    "Publicity Network", "Creator Network", "Business Profile", "Settings"
]

# MOBILE-FRIENDLY MARKET AI NAVIGATION

# Keep existing internal page names so existing features continue working.
HIDDEN_MODULES = [
    "Create Advert",
    "Products",
    "Events",
    "Beauty",
    "Business Services"
]

NAV_LABELS = {
    "AI Video Studio": "AI Creative Studio",
    "Publicity Network": "Market Feed"
}

NAV_ICONS = {
    "Dashboard": "🏠",
    "AI Assistant": "🤖",
    "AI Video Studio": "🎬",
    "Social Hub": "📱",
    "Market Live": "🌍",
    "Campaigns": "📢",
    "Analytics": "📊",
    "Publicity Network": "🏪",
    "Creator Network": "🎨",
    "Business Profile": "👤",
    "Settings": "⚙️"
}

NAV_ITEMS = [
    item for item in MODULES
    if item not in HIDDEN_MODULES
]

if not NAV_ITEMS:
    st.error("No navigation modules are configured.")
    st.stop()

if "market_ai_page" not in st.session_state:
    st.session_state["market_ai_page"] = (
        "Dashboard" if "Dashboard" in NAV_ITEMS
        else NAV_ITEMS[0]
    )

if st.session_state["market_ai_page"] not in NAV_ITEMS:
    st.session_state["market_ai_page"] = (
        "Dashboard" if "Dashboard" in NAV_ITEMS
        else NAV_ITEMS[0]
    )

# TOP BAR
brand_col, menu_col = st.columns([4, 1])

with brand_col:
    st.markdown("### 🌐 MARKET AI")
    st.caption("Every Business Deserves a Voice.")

with menu_col:
    with st.popover("☰ Menu"):
        st.markdown("### Explore MARKET AI")
        st.caption("Select a feature")

        nav_columns = st.columns(2)

        for index, route in enumerate(NAV_ITEMS):
            display_name = NAV_LABELS.get(route, route)
            icon = NAV_ICONS.get(route, "✨")

            with nav_columns[index % 2]:
                if st.button(
                    f"{icon}\n{display_name}",
                    key=f"market_nav_{index}",
                    use_container_width=True
                ):
                    st.session_state["market_ai_page"] = route
                    st.rerun()

# CURRENT PAGE
page = st.session_state["market_ai_page"]

# HOME / BACK NAVIGATION


if page == "Dashboard":
    st.markdown("""
    <div style="
        padding: 45px 25px;
        border-radius: 22px;
        background: linear-gradient(120deg, #10243A, #1677D2, #16A36A);
        color: white;
        margin-bottom: 25px;
    ">
        <h1 style="color:white; font-size:2.4rem;">
            Welcome to MARKET AI 👋
        </h1>
        <h3 style="color:white;">
            Every Business Deserves a Voice.
        </h3>
        <p style="color:white; font-size:1.05rem;">
            Your creative workspace for advertising,
            publicity and business growth.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Your creative workspace")

    st.write(
        "Everything you need to promote your business "
        "is waiting in your menu."
    )

    st.info(
        "☰ Open the Menu above to explore MARKET AI features "
        "and start creating."
    )

    st.divider()

  
    # LIVE NEWS SECTION
    st.markdown("### 🌍 Latest News")
    st.caption("Live headlines from Nigeria and around the world.")

    if st.button("🔄 Refresh news", key="dashboard_refresh_news"):
        st.session_state.pop("dashboard_news", None)
        st.session_state["dashboard_news_index"] = 0

    if "dashboard_news" not in st.session_state:
        dashboard_items = []
        seen_links = set()

        categories = [
            "Nigeria Business",
            "Nigeria Politics",
            "Nigeria News",
            "Technology & AI",
            "Business",
            "Africa",
            "International"
        ]

        with st.spinner("Loading latest headlines..."):
            for category in categories:
                try:
                    for item in get_news(category):
                        link = item.get("link", "")

                        if link and link not in seen_links:
                            seen_links.add(link)
                            dashboard_items.append(item)

                except Exception:
                    continue

        st.session_state["dashboard_news"] = dashboard_items
        st.session_state["dashboard_news_index"] = 0

    @st.fragment(run_every="20s")
    def rotating_dashboard_news():

        items = st.session_state.get("dashboard_news", [])

        if not items:
            st.info("News is temporarily unavailable.")
            return

        start = st.session_state.get("dashboard_news_index", 0)
        visible_items = items[start:start + 2]

        st.session_state["dashboard_news_index"] = (
            start + 2
        ) % len(items)

        for item in visible_items:

            with st.container(border=True):

                image_col, text_col = st.columns([1, 4])

                with image_col:
                    image_url = item.get("image")

                    if image_url:
                        st.image(image_url, width=120)
                    else:
                        st.caption("No image")

                with text_col:
                    st.markdown(
                        f"**{item.get('title', 'News update')}**"
                    )

                    st.caption(
                        f"{item.get('source', 'News source')} · "
                        f"{item.get('published', '')}"
                    )

                    summary = item.get("summary", "")

                    if summary:
                        st.write(summary[:180])

                    link = item.get("link", "")

                    if link and link != "#":
                        st.markdown(f"[Read full story]({link})")

        st.caption("Showing up to two stories · Changes every 20 seconds.")

    rotating_dashboard_news()

    # PUBLIC MARKET FEED
    st.markdown("### 📢 Market Feed")
    st.write(
        "Discover products, services and businesses promoted "
        "by the MARKET AI community."
    )

    st.info(
        "Community adverts will appear here when advertisers "
        "choose to make their campaigns public."
    )


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

elif page in ["Create Advert", "Products", "Events", "Beauty", "Business Services"]:
    section = page if page != "Create Advert" else "All categories"
    header(
        "AI Advert Studio",
        f"Create intelligent advertising campaigns for {section.lower()}."
    )

    st.info(
        "Tell Market AI what you want to promote. "
        "It will prepare the advertising concept and campaign for you."
    )

    category_options = [
        "Product",
        "Church / Ministry",
        "Event / Programme",
        "Business service",
        "School / Education",
        "Beauty & lifestyle",
        "Fashion",
        "Food & beverage",
        "Real estate",
        "Other"
    ]

    default_category = {
        "Products": "Product",
        "Events": "Event / Programme",
        "Beauty": "Beauty & lifestyle",
        "Business Services": "Business service"
    }.get(page, "Product")

    category = st.selectbox(
        "What are you advertising?",
        category_options,
        index=category_options.index(default_category)
    )

    st.divider()

    # CATEGORY-SPECIFIC INFORMATION

    business_name = ""
    offer = ""
    details_parts = []
    uploaded = None
    price = ""

    if category == "Product":
        st.subheader("Product information")

        business_name = st.text_input("Business / brand name")
        offer = st.text_input("Product name *")
        product_description = st.text_area(
            "Describe your product",
            placeholder="Explain what it does, its benefits and important features."
        )
        price = st.text_input("Product price *")
        location = st.text_input("Business location")
        phone = st.text_input("Phone / WhatsApp number")

        uploaded = st.file_uploader(
            "Upload product image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="product_ad_image"
        )

        details_parts = [
            f"Product description: {product_description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    elif category == "Church / Ministry":
        st.subheader("Church and programme information")

        business_name = st.text_input("Church / ministry name")
        programme = st.text_input("Programme name *")
        theme = st.text_input("Programme theme")
        offer = programme

        event_date = st.text_input("Programme date")
        event_time = st.text_input("Programme time")
        venue = st.text_input("Venue / address")
        phone = st.text_input("Church contact number (optional)")

        uploaded = st.file_uploader(
            "Upload church logo or programme flyer (optional)",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            key="church_ad_image"
        )

        details_parts = [
            f"Programme: {programme}",
            f"Theme: {theme}",
            f"Date: {event_date}",
            f"Time: {event_time}",
            f"Venue: {venue}",
            f"Contact: {phone}"
        ]

    elif category == "Event / Programme":
        st.subheader("Event information")

        business_name = st.text_input("Event organiser")
        offer = st.text_input("Event name *")
        event_date = st.text_input("Event date")
        event_time = st.text_input("Event time")
        venue = st.text_input("Event venue")
        price = st.text_input("Ticket price (optional)")
        phone = st.text_input("Contact number")

        uploaded = st.file_uploader(
            "Upload event flyer or image",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            key="event_ad_image"
        )

        details_parts = [
            f"Date: {event_date}",
            f"Time: {event_time}",
            f"Venue: {venue}",
            f"Ticket price: {price}",
            f"Contact: {phone}"
        ]

    elif category == "Business service":
        st.subheader("Business information")

        business_name = st.text_input("Business name")
        offer = st.text_input("What service are you promoting? *")
        description = st.text_area("Describe your services")
        price = st.text_input("Price / starting price (optional)")
        location = st.text_input("Business location")
        phone = st.text_input("Phone / WhatsApp number")

        uploaded = st.file_uploader(
            "Upload business logo or image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="service_ad_image"
        )

        details_parts = [
            f"Services: {description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    elif category == "School / Education":
        st.subheader("School information")

        business_name = st.text_input("School / institution name")
        offer = st.text_input("What are you promoting? *")
        description = st.text_area("Courses, admissions or programmes")
        location = st.text_input("School location")
        phone = st.text_input("Contact number")
        price = st.text_input("Fees (optional)")

        uploaded = st.file_uploader(
            "Upload school logo or flyer (optional)",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            key="school_ad_image"
        )

        details_parts = [
            f"Description: {description}",
            f"Location: {location}",
            f"Contact: {phone}",
            f"Fees: {price}"
        ]

    elif category == "Beauty & lifestyle":
        st.subheader("Beauty and lifestyle information")

        business_name = st.text_input("Business / brand name")
        offer = st.text_input("Product or service name *")
        description = st.text_area("Describe the product or service")
        price = st.text_input("Price (optional)")
        location = st.text_input("Location")
        phone = st.text_input("Phone / WhatsApp number")

        uploaded = st.file_uploader(
            "Upload product or business image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="beauty_ad_image"
        )

        details_parts = [
            f"Description: {description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    elif category == "Fashion":
        st.subheader("Fashion information")

        business_name = st.text_input("Fashion brand / business name")
        offer = st.text_input("What fashion item or service are you promoting? *")
        description = st.text_area("Describe the item or service")
        price = st.text_input("Price (optional)")
        location = st.text_input("Location")
        phone = st.text_input("Contact number")

        uploaded = st.file_uploader(
            "Upload fashion product image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="fashion_ad_image"
        )

        details_parts = [
            f"Description: {description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    elif category == "Food & beverage":
        st.subheader("Food and restaurant information")

        business_name = st.text_input("Restaurant / food business name")
        offer = st.text_input("Food or drink being promoted *")
        description = st.text_area("Describe the food or drink")
        price = st.text_input("Price (if applicable)")
        location = st.text_input("Location")
        phone = st.text_input("Contact number")

        uploaded = st.file_uploader(
            "Upload food or restaurant image (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="food_ad_image"
        )

        details_parts = [
            f"Description: {description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    elif category == "Real estate":
        st.subheader("Property information")

        business_name = st.text_input("Agency / property owner")
        offer = st.text_input("Property type or offer *")
        description = st.text_area("Describe the property")
        price = st.text_input("Property price (optional)")
        location = st.text_input("Property location")
        phone = st.text_input("Contact number")

        uploaded = st.file_uploader(
            "Upload property images (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            key="property_ad_image"
        )

        details_parts = [
            f"Description: {description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    else:
        st.subheader("Advertising information")

        business_name = st.text_input("Business / organisation name")
        offer = st.text_input("What are you promoting? *")
        description = st.text_area("Describe what you are promoting")
        price = st.text_input("Price (optional)")
        location = st.text_input("Location")
        phone = st.text_input("Contact number")

        uploaded = st.file_uploader(
            "Upload an image or flyer (optional)",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            key="other_ad_image"
        )

        details_parts = [
            f"Description: {description}",
            f"Price: {price}",
            f"Location: {location}",
            f"Contact: {phone}"
        ]

    st.divider()

    # CAMPAIGN PREFERENCES

    st.subheader("Advertising preferences")

    audience = st.text_input(
        "Who should this advert reach?",
        placeholder="e.g. families, business owners, young people in Abuja"
    )

    tone = st.selectbox(
        "Advertising style",
        [
            "Let Market AI decide",
            "Professional",
            "Luxury",
            "Energetic",
            "Friendly",
            "Emotional storytelling",
            "Corporate",
            "Cinematic",
            "Minimal and modern"
        ]
    )

    length = st.selectbox(
        "Campaign length",
        ["15 seconds", "30 seconds", "60 seconds", "Social post only"]
    )

    extra_instructions = st.text_area(
        "Anything else Market AI should know? (optional)",
        placeholder="Special instructions, preferred message or creative direction."
    )

    details_parts.append(f"Additional instructions: {extra_instructions}")
    details = "\n".join(
        item for item in details_parts
        if item and not item.endswith(": ")
    )

    # GENERATE ADVERTISING CAMPAIGN

    if st.button("Create my advertising campaign", type="primary"):
        if not offer.strip():
            st.warning("Please tell Market AI what you are promoting.")
        elif category == "Product" and not price.strip():
            st.warning("Please enter your product price.")
        elif category == "Church / Ministry" and not business_name.strip():
            st.warning("Please enter your church or ministry name.")
        else:
            with st.spinner("Market AI is developing your campaign..."):
                result = generate_marketing_copy(
                    category,
                    business_name,
                    offer,
                    audience,
                    details,
                    tone,
                    length,
                    uploaded
                )

            st.session_state["last_ad"] = result
            st.session_state["last_campaign_meta"] = (
                category,
                business_name,
                offer
            )

    # CAMPAIGN PREVIEW AND SAVING

    if "last_ad" in st.session_state:
        st.divider()
        st.subheader("Your Market AI advertising campaign")
        st.markdown(st.session_state["last_ad"])

        if st.button("Save campaign"):
            meta = st.session_state.get(
                "last_campaign_meta",
                ("General", "", "Campaign")
            )

            save_campaign(
                meta[1] or "My business",
                meta[0],
                meta[2],
                st.session_state["last_ad"]
            )

            st.success("Campaign saved successfully.")


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
