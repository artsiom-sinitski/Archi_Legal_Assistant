import logging
import streamlit as st

from openai import OpenAI

import sys
from pathlib import Path
# sys.path.append(rf"{Path(__file__).parent}\archi")
# sys.path.append(rf"{Path(__file__).parent}\archi\src")
# print(f"Path --> {Path(__file__).parent}")

from langchain_openai import ChatOpenAI

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from src.constants import AI_MODELS
import src.docs_processor as dp
from src.prompts import sys_prompt_ru_1

openai_api_key = None
llm_model: str = AI_MODELS.get("gpt_4o_mini")

PAGE_ICON: str = "⚖️"
PAGE_TITLE: str = "Virtual Legal Assistant"

# LANG_EN: str = "EN"
# LANG_RU: str = "RU"dir

# ==== Controls setup =========================================

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
# ==== End Controls setup =====================================

with st.sidebar:
    selected_topic: tuple[str] = st.selectbox("Выбранная тема консультации:",
        ("...", "Расчёт неустойки", "Ответ на вопрос", "Сделать справку", "Резюмировать", "Перевести на другой язык"),
        label_visibility="visible",
        placeholder="..."
    ),
    header = st.columns(1)
    # ------------------------
    header_tile0 = header[0].container(height=None, border=True)
    header_tile0.image("archi/content/img/attorney3.jpg", width=230)
    # ------------------------
    # header_tile1 = header[1].container(height=None, border=False)
    header_tile0.write("💬 Здравствуйте! Меня зовут Арчия")
    header_tile0.write("💬 Я - виртуальный юрист, который может:")
    header_tile0.markdown("* ответить на Ваши вопросы")
    header_tile0.markdown("* предоставить нужные бланки")
    header_tile0.markdown("* дать понятные пошаговые инструкции")
    # st.divider()
# end with

# with st.sidebar
    # pass
    # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    # "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    # "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    # "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
# with end

                       
if "..." in selected_topic[0]:      # enable chat input widget only if topic selected
    chat_prompt = st.chat_input("Сначала выберите тему консультации...", key="DisabledChatPrompt", disabled=True)
else:
    chat_prompt = st.chat_input("Пишите тут...", key="EnabledChatPrompt", disabled=False)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": f'Какова Ваша ситуация (вопрос) по теме "{selected_topic[0]}"?'}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := chat_prompt:
        try:
            openai_api_key = st.secrets.api_credentials.api_key
        except (KeyError, AttributeError) as err:
            logging.info(str(err))

        if not openai_api_key:
            st.info("Your API key is missing or invalid!")
            st.stop()

        client = OpenAI(api_key=openai_api_key)
        PROMPT = PromptTemplate(template=sys_prompt_ru_1, input_variables=["context", "question"])

        llm = ChatOpenAI(
            api_key=openai_api_key,
            temperature=0,
            model=llm_model
        )

        # create the chain to answer questions
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=dp.get_vector_db_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # response = client.chat.completions.create(model=llm_model, messages=st.session_state.messages)
        # assistant_response = response.choices[0].message.content

        response = qa_chain(user_input)
        assistant_response = response.get("result")

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.chat_message("assistant").write(assistant_response)

# if __name__ == "__main__":
#     pass
