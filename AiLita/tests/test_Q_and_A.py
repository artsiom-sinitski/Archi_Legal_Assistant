import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

from pydantic import SecretStr

sys.path.append(rf"{Path(__file__).parent.parent}")

from langchain.chains import RetrievalQA

import AiLita.src.prompts as prompts
import AiLita.src.constants as consts



def main() -> None:
    curr_date: datetime = datetime.now()
    try:
        model_cmd_arg: str = sys.argv[1]
    except IndexError as err:
        print(f"Provide LLM model name as a command line parameter!\n{str(err)}")
        sys.exit(1)
    try:
        llm_model: str = consts.AI_MODELS[model_cmd_arg]
        if "deepseek" in model_cmd_arg:
            from langchain_deepseek import ChatDeepSeek
            import AiLita.src.deepseek_docs_processor_local as dp
            _apikey = "DEEPSEEK_API_KEY"
            llm = ChatDeepSeek(
                api_key=SecretStr(os.environ[_apikey]),
                temperature=0,
                model=llm_model
            )
        elif "gpt" in model_cmd_arg:
            from langchain_openai import ChatOpenAI
            import AiLita.src.openai_docs_processor as dp
            _apikey = "OPENAI_API_KEY"
            llm = ChatOpenAI(
                api_key=SecretStr(os.environ[_apikey]),
                temperature=0,  # 1
                model=llm_model
            )
        else:
            raise Exception("Unknown LLM!")
    except KeyError as err:
        print(err)
        sys.exit(1)

    input_file_path: str = rf"{os.environ['USERDIR']}\Documents\AiLita_knowledge_docs\test_q_and_a\curr_Q-file"
    output_file_path: str = rf"{os.environ['USERDIR']}\Documents\AiLita_knowledge_docs\test_q_and_a"

    q_file_name: list[str] = os.listdir(input_file_path)
    if len(q_file_name) > 1:
        raise ValueError(f"Only 1 file expected, but found -> {len(q_file_name)}")

    full_q_file_path: str = os.path.join(input_file_path, q_file_name[0])
    topic: str = q_file_name[0].split('.')[0]
    # ---------------------------------------------------------------------------------
    PROMPT = prompts.PromptTemplate(
        template=prompts.sys_prompt_to_calculate_penalty_ru,
        input_variables=["context", "question"]
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
    ans_file_name: str = f"Answered_{model_cmd_arg.upper()}_{topic}_{curr_date.strftime('%Y%m%d')}.txt"

    # list documents used to acquire the knowledge
    files: list[str] = os.listdir(dp.knowledge_docs_path)
    files = sorted([fi for fi in files if os.path.isfile(f"{dp.knowledge_docs_path}/{fi}")])

    # calculated number of tokens for the prompt
    prompt_tokens_num = prompts.calculate_tokens_num(llm_model, PROMPT.template)
    print(f"{prompt_tokens_num = }", end='\n\n')
    # -----------------------------------------------------------------------------------------------------
    start_time: float = 0.0
    end_time: float = 0.0

    input_tokens_total: float = 0.0
    input_tokens_total_price: float = 0.0

    output_tokens_total: float = 0.0
    output_tokens_total_price: float = 0.0

    answer_grand_total_price: float = 0.0
    grand_total_amount: float = 0.0

    input_tokens_rate: float = consts.model_price_catalog[model_cmd_arg][consts.INPUT_TOKENS_PRICE_1M] / consts.ONE_MILLION
    output_tokens_rate: float = consts.model_price_catalog[model_cmd_arg][consts.OUTPUT_TOKENS_PRICE_1M] / consts.ONE_MILLION
    # ------------------------------------------------------------------------------------------------------------------

    with open(fr"{output_file_path}\{ans_file_name}", 'w', encoding="utf-8") as out_fp:
        out_fp.write(f"REPORT DATE:\t{curr_date.strftime('%Y-%m-%d %H:%M')}\n")
        out_fp.write(f"LLM MODEL:\t{model_cmd_arg}\n")
        out_fp.write(f"ENCODING:\t{consts.WIN_ENCODING_RU}\n")
        out_fp.write(f"Q-FILE:\t{q_file_name[0]}\n")
        out_fp.write(f"LAW DOCS:\t{len(files)}\n")
        out_fp.writelines([f"\t - {file}\n" for file in files])
        out_fp.write(f"\nPROMPT:{prompts.sys_prompt_to_calculate_penalty_ru}")
        out_fp.write(f"\n{'#'*70}\n")

        print(f"{'*'*3} Started processing questions...")
        run_time_start: float = time.perf_counter()
        response: dict[str, any] = {}

        for idx, question in enumerate(questions, start=1):
            start_time = time.perf_counter()
            # Dict 'response' has 3 keys -> {'query': str, 'result': str, 'source_documents': list}
            response = qa_chain(question)

            q_tokens_num = prompts.calculate_tokens_num(llm_model, question)
            print(f"\n\t{q_tokens_num = }")

            input_tokens_total = prompt_tokens_num + q_tokens_num
            input_tokens_total_price = input_tokens_total * input_tokens_rate
            print(f"\t{round(input_tokens_total_price, 5) = }")

            output_tokens_total = prompts.calculate_tokens_num(llm_model, str(response))
            print(f"\t{output_tokens_total = }")

            output_tokens_total_price = output_tokens_total * output_tokens_rate
            print(f"\t{round(output_tokens_total_price, 5) = }")

            answer_grand_total_price = input_tokens_total_price + output_tokens_total_price
            print(f"\t{round(answer_grand_total_price, 5) = }")

            grand_total_amount += answer_grand_total_price

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
        run_time_end: float = time.perf_counter() - run_time_start
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(run_time_end))
        out_fp.write(f"\n{'-'*99}\n")
        out_fp.write(f"\tTotal Run Time:\t{elapsed_time}\n")
        out_fp.write(f"\tGrand Total Cost:\t${round(grand_total_amount, 2)}")
    # with end
    print(f"{'*' * 3} Finished processing questions {'*' * 3}")


if __name__ == "__main__":
    main()
