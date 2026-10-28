import streamlit as st
import sqlite3
import uuid
from pathlib import Path

from database import register_visitor, get_all_visitors, DB_PATH


# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="FacePass AI",
    page_icon="🎨",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "visitor_photos"
UPLOAD_DIR.mkdir(exist_ok=True)


# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #111111;
    color: #F5F0E8;
}

[data-testid="stSidebar"] {
    background-color: #1B1B1B;
}

h1, h2, h3 {
    color: #D4AF70 !important;
}

p, label, span {
    color: #F5F0E8;
}

div.stButton > button {
    background-color: #D4AF70;
    color: #111111;
    border-radius: 10px;
    border: none;
    padding: 10px 22px;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #F0D49A;
    color: #111111;
}

.card {
    background-color: #202020;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #55452B;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

st.sidebar.markdown("# 🎨 FacePass AI")
st.sidebar.caption("Your Personalized Art Gallery")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Home",
        "Register Visitor",
        "Recognize Visitor",
        "Registered Visitors",
        "Art Gallery",
        "About Project"
    ]
)


# ---------------- HOME ----------------

if page == "Home":

    st.markdown("# 🎨 FacePass AI")
    st.markdown("### Every visit tells a story.")

    st.markdown("""
    <div class="card">
        <h2>Welcome to Your Smart Art Gallery</h2>
        <p>
        FacePass AI is a visitor personalization prototype
        designed to help an art gallery remember registered
        visitors and recommend artworks based on their interests.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 👤 Visitor Profiles")
        st.write("Register visitors with their consent.")

    with col2:
        st.markdown("### 🔍 Recognition")
        st.write("Check uploaded photographs against registered profiles.")

    with col3:
        st.markdown("### 🖼️ Art Discovery")
        st.write("Explore artworks based on personal interests.")

    st.info(
        "This is a student prototype. Register only consenting "
        "volunteers and use their photographs responsibly."
    )


# ---------------- REGISTER VISITOR ----------------

elif page == "Register Visitor":

    st.markdown("# 👤 Register a Visitor")
    st.write("Create a personalized gallery visitor profile.")

    with st.form("visitor_registration"):

        name = st.text_input("Visitor Name")

        interests = st.multiselect(
            "Select Art Interests",
            [
                "Modern Art",
                "Traditional Art",
                "Photography",
                "Sculpture",
                "Abstract Art",
                "Nature",
                "Portraits",
                "Digital Art"
            ]
        )

        photograph = st.file_uploader(
            "Upload Visitor Photograph",
            type=["jpg", "jpeg", "png"]
        )

        consent = st.checkbox(
            "I have permission from this volunteer to store "
            "and process their photograph for this demonstration."
        )

        submitted = st.form_submit_button("Register Visitor")

    if submitted:

        if not name.strip():
            st.error("Please enter your name.")

        elif not interests:
            st.error("Please select at least one interest.")

        elif photograph is None:
            st.error("Please upload a photograph.")

        elif not consent:
            st.error("Consent is required.")

        else:

            file_extension = (
                Path(photograph.name).suffix.lower() or ".jpg"
            )

            photo_filename = (
                f"{uuid.uuid4().hex}{file_extension}"
            )

            photo_path = UPLOAD_DIR / photo_filename

            with open(photo_path, "wb") as photo_file:
                photo_file.write(photograph.getbuffer())

            visitor_id = register_visitor(
                name.strip(),
                interests,
                photo_path
            )

            st.success("Visitor registered successfully!")

            st.write(f"**Visitor ID:** {visitor_id}")
            st.write(f"**Name:** {name.strip()}")
            st.write(f"**Interests:** {', '.join(interests)}")

            st.image(
                str(photo_path),
                caption="Registered visitor photograph",
                width=220
            )


# ---------------- RECOGNIZE VISITOR ----------------

elif page == "Recognize Visitor":

    st.markdown("# 🔍 Returning Visitor Recognition")

    st.markdown("""
    <div class="card">
        <h3>Welcome Back to the Gallery</h3>
        <p>
        Upload a consenting, registered volunteer's photograph
        to check for a possible match.
        </p>
    </div>
    """, unsafe_allow_html=True)

    photograph = st.file_uploader(
        "Upload Visitor Photograph",
        type=["jpg", "jpeg", "png"],
        key="recognition_upload"
    )

    if photograph is not None:

        st.image(
            photograph,
            caption="Uploaded photograph",
            width=220
        )

        if st.button("Find Visitor"):

            temporary_path = (
                UPLOAD_DIR / f"check_{uuid.uuid4().hex}.jpg"
            )

            with open(temporary_path, "wb") as photo_file:
                photo_file.write(photograph.getbuffer())

            try:
                from deepface import DeepFace

                with sqlite3.connect(DB_PATH) as connection:
                    visitors = connection.execute(
                        """
                        SELECT visitor_id, name, interests,
                               photograph_path
                        FROM visitors
                        """
                    ).fetchall()

                match_found = False

                with st.spinner("Checking registered profiles..."):

                    for visitor in visitors:

                        visitor_id, name, interests, saved_photo = visitor

                        if not Path(saved_photo).is_file():
                            continue

                        try:
                            result = DeepFace.verify(
                                img1_path=str(temporary_path),
                                img2_path=str(saved_photo),
                                enforce_detection=True,
                                detector_backend="opencv",
                                silent=True
                            )

                            if result.get("verified", False):

                                match_found = True

                                st.success("Possible match found!")
                                st.subheader(f"Welcome back, {name}!")
                                st.write(f"**Visitor ID:** {visitor_id}")
                                st.write(f"**Interests:** {interests}")

                                st.markdown("### Recommended Artworks")

                                interest_list = [
                                    item.strip()
                                    for item in interests.split(",")
                                ]

                                recommendations = {
                                    "Modern Art": "Contemporary Expressions",
                                    "Traditional Art": "Classical Heritage",
                                    "Photography": "Moments in Time",
                                    "Sculpture": "Three-Dimensional Stories",
                                    "Abstract Art": "Beyond Reality",
                                    "Nature": "Nature's Canvas",
                                    "Portraits": "Faces and Stories",
                                    "Digital Art": "The Digital Imagination"
                                }

                                for interest in interest_list:
                                    if interest in recommendations:
                                        st.write(
                                            "🖼️ " +
                                            recommendations[interest]
                                        )

                                break

                        except Exception:
                            continue

                if not match_found:
                    st.warning(
                        "No matching registered profile was found. "
                        "The result is not a definitive identity decision."
                    )

            except ImportError:
                st.error(
                    "DeepFace is not installed in the active Python "
                    "environment. Install it before using recognition."
                )

            except Exception as error:
                st.error("Recognition could not be completed.")
                st.caption(str(error))

            finally:
                if temporary_path.exists():
                    temporary_path.unlink()


# ---------------- REGISTERED VISITORS ----------------

elif page == "Registered Visitors":

    st.markdown("# 👥 Registered Visitors")

    visitors = get_all_visitors()

    if not visitors:
        st.info("No visitors have registered yet.")

    else:
        st.write(f"**Total Registered Visitors:** {len(visitors)}")

        for visitor in visitors:

            visitor_id, name, interests, created_at = visitor

            with st.container(border=True):

                st.subheader(name)
                st.write(f"**Visitor ID:** {visitor_id}")
                st.write(f"**Interests:** {interests}")
                st.caption(f"Registration date: {created_at}")


# ---------------- ART GALLERY ----------------

elif page == "Art Gallery":

    st.markdown("# 🖼️ Explore the Art Gallery")

    artworks = [
        {
            "title": "Contemporary Expressions",
            "category": "Modern Art",
            "description": "Discover bold ideas and contemporary creativity."
        },
        {
            "title": "Classical Heritage",
            "category": "Traditional Art",
            "description": "Explore artistic traditions and cultural heritage."
        },
        {
            "title": "Moments in Time",
            "category": "Photography",
            "description": "Experience stories captured through photography."
        },
        {
            "title": "Three-Dimensional Stories",
            "category": "Sculpture",
            "description": "Explore form, texture and three-dimensional art."
        },
        {
            "title": "Beyond Reality",
            "category": "Abstract Art",
            "description": "Discover shapes, colours and abstract expression."
        },
        {
            "title": "Nature's Canvas",
            "category": "Nature",
            "description": "Celebrate the beauty of the natural world."
        },
        {
            "title": "Faces and Stories",
            "category": "Portraits",
            "description": "Explore portraits that express human stories."
        },
        {
            "title": "The Digital Imagination",
            "category": "Digital Art",
            "description": "Discover creativity through digital media."
        }
    ]

    for row in range(0, len(artworks), 2):

        col1, col2 = st.columns(2)

        for col, artwork in zip(
            [col1, col2],
            artworks[row:row + 2]
        ):

            with col:
                with st.container(border=True):

                    st.markdown(
                        f"### 🎨 {artwork['title']}"
                    )

                    st.caption(artwork["category"])
                    st.write(artwork["description"])


# ---------------- ABOUT PROJECT ----------------

elif page == "About Project":

    st.markdown("# ℹ️ About FacePass AI")

    st.markdown("""
    <div class="card">
        <h3>Project Objective</h3>
        <p>
        FacePass AI demonstrates how a smart gallery can maintain
        consenting visitor profiles and provide interest-based
        artwork recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Capabilities")

    st.write("✅ Visitor registration and consent collection")
    st.write("✅ SQLite database storage")
    st.write("✅ Facial comparison against registered photographs")
    st.write("✅ Interest-based artwork recommendations")
    st.write("✅ Visitor profile listing")

    st.markdown("### Technologies")

    st.write("Python, Streamlit, SQLite, OpenCV and DeepFace")

    st.markdown("### Limitations")

    st.write(
        "This is an educational prototype. Facial comparison can "
        "produce false matches or missed matches. It must not be "
        "used as the sole basis for identity or security decisions."
    )

    st.write(
        "Use consenting volunteers, protect stored photographs, "
        "and delete test records and images when no longer needed."
    )
