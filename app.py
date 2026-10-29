import httpx
import streamlit as st
from openai import OpenAI
from PIL import Image

st.title("RX Pizzeria")

# Initialize OpenAI client
@st.cache_resource
def get_openai_client(api_key):
    return OpenAI(
        api_key=api_key,
        http_client=httpx.Client()
    )

client = get_openai_client(st.secrets["OPENAI_API_KEY"])

# System instructions
grounding = st.secrets["GROUNDING"]

# Display logo
image = Image.open("logo.png")
st.image(image)

# Initialize model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-5-mini"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("How can I help you today?"):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.responses.create(
                model=st.session_state["openai_model"],
                instructions=grounding,
                input=[
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            for event in response:
                if event.type == "response.output_text.delta":
                    full_response += event.delta

                    message_placeholder.markdown(
                        full_response + "▌"
                    )

            message_placeholder.markdown(full_response)

            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            st.session_state.messages.pop()
