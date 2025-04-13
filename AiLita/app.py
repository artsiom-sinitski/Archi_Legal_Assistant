import logging
import streamlit as st

from openai import OpenAI

import sys
from pathlib import Path
# sys.path.append(rf"{Path(__file__).parent}\AiLita")
# sys.path.append(rf"{Path(__file__).parent}\AiLita\src")
# print(f"Path --> {Path(__file__).parent}")

from langchain_openai import ChatOpenAI

from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate

from AiLita.src.prompts import *
import AiLita.src.constants as consts
import AiLita.src.docs_processor as dp


openai_api_key = None
# llm_model: str = consts.AI_MODELS.get("gpt_4o_mini")
llm_model: str = consts.AI_MODELS.get("gpt_o1")

PAGE_ICON: str = "⚖️"
PAGE_TITLE: str = "Virtual Legal Assistant"

# LANG_EN: str = "EN"
# LANG_RU: str = "RU"dir

# ==== Controls setup =========================================

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
# ==== End Controls setup =====================================

empty_opt: str = "..."
penalty_opt: str = "Некачественный товар"
question_opt: str = "Покупка товара"
merch_return_opt: str = "Возврат товара"
# resume_opt: str = "Резюмировать"
# translate_opt: str = "Перевести на другой язык"

with st.sidebar:
    selected_topic: tuple[str] = st.selectbox("Выбранная тема консультации:",
        (empty_opt, penalty_opt, question_opt, merch_return_opt),
        label_visibility="visible",
        placeholder="..."
    ),
    header = st.columns(1)
    # ------------------------
    header_tile0 = header[0].container(height=None, border=True)
    header_tile0.image("AiLita/content/img/attorney3.jpg", width=230)
    # ------------------------
    # header_tile1 = header[1].container(height=None, border=False)
    header_tile0.write("💬 Здравствуйте! Меня зовут Аилита")
    header_tile0.write("💬 Я - виртуальный юрист, который может:")
    header_tile0.markdown("* ответить на Ваши вопросы")
    header_tile0.markdown("* предоставить нужные бланки")
    header_tile0.markdown("* дать понятные пошаговые инструкции")
    # st.divider()
# end with

                       
if empty_opt in selected_topic[0]:      # enable chat input widget only if a topic selected
    chat_prompt_widget = st.chat_input("Сначала выберите тему консультации...", key="DisabledChatPrompt", disabled=True)
    st.empty()
else:
    chat_prompt_widget = st.chat_input("Пишите тут...", key="EnabledChatPrompt", disabled=False)

    # with st.container():
    #     st.button("Голосовой Ввод")
    #     st.button("Сохранить Консультацию")
    #     st.button("Загрузить Файл...")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": f'Какова Ваша ситуация (вопрос) по теме "{selected_topic[0]}"?'}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := chat_prompt_widget:
        try:
            openai_api_key = st.secrets.api_credentials.api_key
        except (KeyError, AttributeError) as err:
            logging.info(str(err))

        if not openai_api_key:
            st.info("Your API key is missing or invalid!")
            st.stop()

        client = OpenAI(api_key=openai_api_key)

        # match(selected_topic[0]):
        #     case penalty_opt: pmpt_template = cnst.topic_2_prompt_mapping.get("penalty_prompt")
        #     case question_opt: pmpt_template = cnst.topic_2_prompt_mapping.get("question_prompt")
        #     case _: pmpt_template = cnst.topic_2_prompt_mapping.get("question_prompt")
        if penalty_opt == selected_topic[0]:
            pmpt_template = consts.topic_2_prompt_mapping.get("penalty_prompt")
        elif question_opt == selected_topic[0]:
            pmpt_template = consts.topic_2_prompt_mapping.get("question_prompt")
        elif merch_return_opt == selected_topic[0]:
            pmpt_template = consts.topic_2_prompt_mapping.get("merch_return_prompt")
        else:
            pmpt_template = consts.topic_2_prompt_mapping.get("question_prompt")

        PROMPT = PromptTemplate(
            template=pmpt_template,
            input_variables=["context", "question"]
        )

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
