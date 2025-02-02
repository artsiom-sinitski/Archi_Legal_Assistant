import os
import sys
import json
import time
from datetime import datetime

from pathlib import Path
sys.path.append(rf"{Path(__file__).parent.parent}")

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

import archi.src.prompts as prompts
import archi.src.constants as consts
import archi.src.docs_processor as dp


def main() -> None:
    curr_date: datetime = datetime.now()
    openai_api_key: str = os.environ["OPENAI_API_KEY"]

    try:
        model_cmd_arg: str = sys.argv[1]
    except IndexError as err:
        print("Provide LLM model name as a command line parameter!")
        sys.exit(1)
    try:
        llm_model: str = consts.AI_MODELS[model_cmd_arg]
    except KeyError as err:
        print(err)
        sys.exit(1)

    input_file_path: str = rf"{os.environ['USERDIR']}\Documents\archi_knowledge_docs\test_q_and_a\curr_Q-file"
    output_file_path: str = rf"{os.environ['USERDIR']}\Documents\archi_knowledge_docs\test_q_and_a"

    q_file_name: list[str] = os.listdir(input_file_path)
    if len(q_file_name) > 1:
        raise ValueError(f"Only 1 file expected at this location, but found -> {len(q_file_name)}")

    full_q_file_path: str = os.path.join(input_file_path, q_file_name[0])
    topic: str = q_file_name[0].split('.')[0]
    # ---------------------------------------------------------------------------------
    PROMPT = prompts.PromptTemplate(
        template=prompts.sys_prompt_to_calculate_penalty_ru,
        input_variables=["context", "question"]
    )

    llm = ChatOpenAI(
        api_key=openai_api_key,
        temperature=1, # 0
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
    # ------------------------------------------------------------------------------

    with open(fr"{full_q_file_path}", 'r', encoding=consts.WIN_ENCODING_RU) as in_fp:
        data = json.load(in_fp)

    questions: list[str] = data.get("Questions")
    ans_file_name: str = f"Answered_{llm_model.upper()}_{len(questions)}qs_{topic}_{curr_date.strftime('%Y%m%d')}.txt"

    # list documents used to acquire the knowledge
    files: list[str] = os.listdir(dp.knowledge_docs_path)
    files = sorted([fi for fi in files if os.path.isfile(dp.knowledge_docs_path + '/' + fi)])

    # calculated number of tokens for the prompt
    prompt_tokens_num = prompts.calculate_tokens_num(llm_model, PROMPT.template)
    print(f"{prompt_tokens_num = }", end='\n\n')
    # -----------------------------------------------------------------------------------------------------
    start_time: float = 0.0
    end_time: float = 0.0
    elapsed_time: str = ""
    input_tokens_total: float = 0.0
    input_tokens_total_price: float = 0.0
    output_tokens_total: float = 0.0
    output_tokens_total_price: float = 0.0
    answer_grand_total_price: float = 0.0
    input_tokens_rate: float = consts.model_price_catalog[llm_model][consts.INPUT_TOKENS_PRICE_1K] / 1000
    output_tokens_rate: float = consts.model_price_catalog[llm_model][consts.OUTPUT_TOKENS_PRICE_1K] / 1000
    # -----------------------------------------------------------------------------------------------------
    with open(fr"{output_file_path}\{ans_file_name}", 'w', encoding="utf-8") as out_fp:
        out_fp.write(f"DATE:\t{curr_date.strftime('%Y-%m-%d %H:%M')}\n")
        out_fp.write(f"LLM MODEL:\t{llm_model}\n")
        out_fp.write(f"ENCODING:\t{consts.WIN_ENCODING_RU}\n")
        out_fp.write(f"Q-FILE:\t{q_file_name[0]}\n")
        out_fp.write(f"DOCS:\t{len(files)}\n")
        out_fp.writelines([f"\t - {file}\n" for file in files])
        out_fp.write(f"\nPROMPT:{prompts.sys_prompt_to_calculate_penalty_ru}")
        out_fp.write(f"\n{'#'*70}\n")

        print(f"{'*'*3} Started processing questions...")
        response: dict[str, any] = {}

        for idx, question in enumerate(questions, start=1):
            start_time = time.perf_counter()

            # Dict 'response' has 3 keys -> {'query': str, 'result': str, 'source_documents': list}
            response = qa_chain(question)

            # print(f"{len(question) = }")
            # print(f"{len(response['query']) = }")
            q_tokens_num = prompts.calculate_tokens_num(llm_model, question)
            print(f"\n\t{q_tokens_num = }")

            input_tokens_total = prompt_tokens_num + q_tokens_num
            input_tokens_total_price = input_tokens_total * input_tokens_rate
            print(f"\t{input_tokens_total_price = }")

            output_tokens_total = prompts.calculate_tokens_num(llm_model, response)
            print(f"\t{output_tokens_total = }")

            output_tokens_total_price = output_tokens_total * output_tokens_rate
            print(f"\t{output_tokens_total_price = }")

            answer_grand_total_price = input_tokens_total_price + output_tokens_total_price
            print(f"\t{answer_grand_total_price = }")

            end_time = time.perf_counter() - start_time
            elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time))

            out_fp.write(f"Q{idx} - \n")
            out_fp.writelines([f"Cost: ${round(answer_grand_total_price, 5)}\nTime: {elapsed_time}\n"])
            out_fp.writelines([f"{'-' * 15}\n", f"{question}\n\n", "Answer:\n"])
            try:
                out_fp.write(response.get("result"))
            except Exception as ex:
                print(f"\t{'*'*3} {ex}")
            out_fp.write(f"\n\n{'-'*99}\n")
            print(f"Processed Q{idx} (${round(answer_grand_total_price, 5)} | {elapsed_time}) -> {question}")
        # for end
        print(f"{'*' * 3} Finished processing questions {'*' * 3}")
    # with end


if __name__ == "__main__":
    main()
