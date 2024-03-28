from openai import OpenAI
import streamlit as st
import logging


PAGE_ICON: str = "⚖️"
PAGE_TITLE: str = "Virtual Legal Assistant"

# LANG_EN: str = "EN"
# LANG_RU: str = "RU"
# AI_MODEL_OPTIONS: list[str] = [
#     "gpt-4-1106-preview",
#     "gpt-4-vision-preview",
#     "gpt-4",
#     "gpt-4-32k",
#     "gpt-3.5-turbo-1106",
#     "gpt-3.5-turbo",
#     "gpt-3.5-turbo-16k",
# ]

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

with st.sidebar:
    # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    # "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    # "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

header = st.columns(2)
# ------------------------
header_tile0 = header[0].container(height=None, border=False)
header_tile0.image("content/img/attorney2.jpg", width=260)
# ------------------------
header_tile1 = header[1].container(height=None, border=False)

header_tile1.write("💬 Арчия к Вашим услугам! Она поможет:")
# header_tile1.write("💬 Archie is at Your service! She would be able to:")
header_tile1.divider()
header_tile1.markdown("* ответить на Ваши вопросы")
# header_tile1.markdown("* answer your legal questions")
header_tile1.markdown("* предоставить нужные бланки")
# header_tile1.markdown("* provide You with document templates")
header_tile1.markdown("* дать понятные пошаговые инструкции")
# header_tile1.markdown("* give step-by-step instructions for Your case")

st.divider()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Чем я могу Вам помочь?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

openai_api_key = None
if prompt := st.chat_input():
    try:
        # OpenAI.api_key = st.secrets.api_credentials.api_key
        openai_api_key = st.secrets.api_credentials.api_key
    except (KeyError, AttributeError) as err:
        pass
        # st.error(st.session_state.locale.empty_api_handler)
        logging.info(str(err))

    if not openai_api_key:
        st.info("Your API key is missing or invalid!")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

# if __name__ == "__main__":
#     pass
