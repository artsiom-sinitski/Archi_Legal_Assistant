import os
import sys
import json
import time
from datetime import datetime

from pathlib import Path
sys.path.append(rf"{Path(__file__).parent.parent}")

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from archi.src.constants import (WIN_ENCODING_RU, AI_MODELS)
from archi.src.prompts import sys_prompt_to_calculate_penalty_ru
import archi.src.docs_processor as dp

# --------------------------------------
openai_api_key: str = os.environ["OPENAI_API_KEY"]
llm_model: str = AI_MODELS.get("gpt4o1")
# --------------------------------------


def main() -> None:
    start_time: float = 0.0
    end_time: float = 0.0
    elapsed_time: str = ""
    curr_date: datetime = datetime.now()

    input_file_path: str = rf"{os.environ['USERDIR']}\Documents\archi_knowledge_docs\test_q_and_a\curr_Q-file"
    output_file_path: str = rf"{os.environ['USERDIR']}\Documents\archi_knowledge_docs\test_q_and_a"
    q_file_name: list[str] = os.listdir(input_file_path)

    if len(q_file_name) > 1:
        raise ValueError(f"Only 1 file expected at this location, but found -> {len(q_file_name)}")

    full_q_file_path = os.path.join(input_file_path, q_file_name[0])
    topic = q_file_name[0].split('.')[0]
    ans_file_name = f"Answers_to_{topic}_{curr_date.strftime('%Y%m%d')}.txt"
    # ---------------------------------------------------------------------------------
    # sys_prompt_ru_1
    PROMPT = PromptTemplate(template=sys_prompt_to_calculate_penalty_ru, input_variables=["context", "question"])

    llm = ChatOpenAI(
        api_key=openai_api_key,
        temperature=1,   #0
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
    # ---------------------------------------------------------------------------------

    with open(fr"{full_q_file_path}", 'r', encoding=WIN_ENCODING_RU) as fp:
        data = json.load(fp)

    questions = data.get("Questions")

    with open(fr"{output_file_path}\{ans_file_name}", 'w', encoding="utf-8") as fp:
        fp.write(f"    DATE:\t{curr_date.strftime('%Y-%m-%d %H:%M')}\n")
        fp.write(f"ENCODING:\t{WIN_ENCODING_RU}\n")
        fp.write(f"  Q-FILE:\t{q_file_name[0]}\n")
        fp.write(f"  PROMPT:\n{sys_prompt_to_calculate_penalty_ru}")
        fp.write(f"\n{'#'*70}\n")

        print(f"{'*'*3} Started processing questions...")
        for idx, question in enumerate(questions, start=1):
            start_time = time.perf_counter()
            response = qa_chain(question)
            end_time = time.perf_counter() - start_time
            elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time))

            fp.writelines([f"Q{idx} - {elapsed_time} |\n", f"{'-'*15}\n", f"{question}\n\n", "Answer:\n"])
            try:
                fp.write(response.get("result"))
            except Exception as ex:
                print(f"\t{'*'*3} {ex}")
            fp.write(f"\n\n{'-'*99}\n")
            print(f"\tProcessed Q{idx} ({elapsed_time}) -> {question}")
        # for end
        print(f"{'*' * 3} Finished processing questions {'*' * 3}")
    # with end


if __name__ == "__main__":
    main()
