import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import SecretStr
from spire.doc import (
    FileFormat, Section, Document
)

sys.path.append(rf"{Path(__file__).parent.parent}")

from langchain.chains import RetrievalQA

import AiLita.src.prompts as prompts
import AiLita.src.constants as consts
import AiLita.src.deepseek_docs_processor_local as dp

# ====  Function Definitions ============================================================
# =======================================================================================

def setup() -> dict[str, Any]:
    test_params: dict[str, Any] = dict()
    test_params["report_date"] = datetime.now().strftime('%Y%m%d')
    test_params["report_ts"] = datetime.now().strftime('%Y-%m-%d %H:%M')
    try:
        test_params["model_argv"] = sys.argv[1]
    except IndexError as err:
        print(f"Provide LLM model name as a command line parameter!\n{str(err)}")
        sys.exit(1)
    try:
        test_params["model_name_no_params"] = test_params["model_argv"].split(':')[0]   # remove the parameters number
        test_params["llm_model"] = consts.AI_MODELS[test_params["model_name_no_params"]]
        temperature: int = 0
        if "deepseek" in test_params["model_argv"]:
            from langchain_deepseek import ChatDeepSeek
            import AiLita.src.deepseek_docs_processor_local as dp
            _apikey = "DEEPSEEK_API_KEY"
            llm = ChatDeepSeek(
                api_key=SecretStr(os.environ[_apikey]),
                temperature=temperature,
                model=test_params["llm_model"]
            )
        elif "gpt" in test_params["model_argv"]:
            from langchain_openai import ChatOpenAI
            import AiLita.src.openai_docs_processor as dp
            _apikey = "OPENAI_API_KEY"
            llm = ChatOpenAI(
                api_key=SecretStr(os.environ[_apikey]),
                temperature=temperature,
                model=test_params["llm_model"]
            )
        else:
            raise Exception("Unknown LLM!")
        test_params["llm_obj"] = llm
    except KeyError as err:
        print(err)
        sys.exit(1)

    test_params["input_file_path"] = rf"{os.environ['USERDIR']}\Documents\AiLita_knowledge_docs\test_q_and_a\curr_Q-file"
    test_params["output_file_path"] = rf"{os.environ['USERDIR']}\Documents\AiLita_knowledge_docs\test_q_and_a"

    q_file_name: list[str] = os.listdir(test_params["input_file_path"])
    if len(q_file_name) != 1:
        raise ValueError(f"Expected Only 1 file, but found -> {len(q_file_name)}")

    if q_file_name[0].endswith(".json"):
        test_params["q_file_type"] = "json"
        test_params["prompt_text"] = prompts.sys_prompt_to_calculate_penalty_ru
    elif q_file_name[0].endswith(".docx") and "иск" in q_file_name[0]:
        test_params["q_file_type"] = "docx"
        test_params["prompt_text"] = prompts.sys_prompt_to_prepare_claim_ru
    else:
        raise ValueError("Unknown q-file type!")

    test_params["q_file_name"] = q_file_name[0]
    test_params["full_q_file_path"] = os.path.join(test_params["input_file_path"], q_file_name[0])
    test_params["topic"] = q_file_name[0].split('.')[0]
    # --------------------------------------------------------------------------------------------
    test_params["prompt_template"] = prompts.PromptTemplate(
        template=test_params["prompt_text"],
        input_variables=["context", "question"]
    )
    return test_params



def answer_law_questions(test_params: dict[str, Any], qa_chain) -> None:
    run_time_start: float = time.perf_counter()

    with open(fr"{test_params['full_q_file_path']}", 'r', encoding=consts.WIN_ENCODING_RU) as in_fp:
        data = json.load(in_fp)

    questions: list[str] = data.get("Questions")
    ans_file_name: str =\
        f"Answered_{test_params["model_name_no_params"].upper()}_{test_params["topic"]}_{test_params["report_date"]}.txt"

    with open(fr"{test_params["output_file_path"]}\{ans_file_name}", 'w', encoding="utf-8") as out_fp:
        out_fp.write(f"REPORT DATE:\t{test_params["report_ts"]}\n")
        out_fp.write(f"LLM MODEL:\t{test_params["model_argv"]}\n")
        out_fp.write(f"ENCODING:\t{consts.WIN_ENCODING_RU}\n")
        out_fp.write(f"Q-FILE:\t{test_params["q_file_name"]}\n")
        out_fp.write(f"LAW DOCS:\t{len(test_params["knowledge_files"])}\n")
        out_fp.writelines([f"\t - {file}\n" for file in test_params["knowledge_files"]])
        out_fp.write(f"\nPROMPT:{test_params["prompt_text"]}")
        out_fp.write(f"\n{'#'*70}\n")

        response: dict[str, Any] = {}

        for idx, question in enumerate(questions, start=1):
            start_time = time.perf_counter()
            # Dict 'response' has 3 keys -> {'query': str, 'result': str, 'source_documents': list}
            response = qa_chain.invoke(question)

            q_tokens_num = prompts.calculate_tokens_num(test_params["llm_model"], question)
            print(f"\n\t{q_tokens_num = }")

            # input_tokens_total = prompt_tokens_num + q_tokens_num
            # input_tokens_total_price = input_tokens_total * input_tokens_rate
            # print(f"\t{round(input_tokens_total_price, 5) = }")

            output_tokens_total = prompts.calculate_tokens_num(test_params["llm_model"], str(response))
            print(f"\t{output_tokens_total = }")

            # output_tokens_total_price = output_tokens_total * output_tokens_rate
            # print(f"\t{round(output_tokens_total_price, 5) = }")

            # answer_grand_total_price = input_tokens_total_price + output_tokens_total_price
            # print(f"\t{round(answer_grand_total_price, 5) = }")

            # grand_total_amount += answer_grand_total_price

            end_time = time.perf_counter() - start_time
            elapsed_time = time.strftime("%H:%M:%S", time.gmtime(end_time))

            out_fp.write(f"Q{idx} - \n")
            # out_fp.writelines([f"Cost: ${round(answer_grand_total_price, 5)}\nTime: {elapsed_time}\n"])
            out_fp.writelines([f"{'-' * 15}\n", f"{question}\n\n", "Answer:\n"])
            try:
                out_fp.write(response.get("result"))
            except Exception as ex:
                print(f"\t{'*'*3} {ex}")
            out_fp.write(f"\n\n{'-'*99}\n")
            # print(f"Processed Q{idx} (${round(answer_grand_total_price, 5)} | {elapsed_time}) -> {question}")
        # for end
        run_time_end: float = time.perf_counter() - run_time_start
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(run_time_end))
        out_fp.write(f"\n{'-'*99}\n")
        out_fp.write(f"\tTotal Run Time:\t{elapsed_time}\n")
        # out_fp.write(f"\tGrand Total Cost:\t${round(grand_total_amount, 2)}")
    # with end
# def end


def produce_court_claim(test_params: dict[str, Any], qa_chain) -> None:
    run_time_start: float = time.perf_counter()
    ans_file_name: str = \
        rf"Answered_{test_params["model_name_no_params"].upper()}_{test_params["topic"]}_{test_params["report_date"]}.docx"

    in_doc: Document = Document()
    in_doc.LoadFromFile(rf"{test_params["input_file_path"]}\{test_params["q_file_name"]}")

    response: dict[str, Any] = qa_chain.invoke(in_doc.GetText())

    # Save LLM response to a doc file
    out_doc: Document = Document()
    section: Section = out_doc.AddSection()
    section.PageSetup.Margins.All = 40

    out_doc_header = section.AddParagraph()
    out_doc_header.AppendText(f"REPORT DATE:\t{test_params["report_ts"]}\n")
    out_doc_header.AppendText(f"LLM MODEL:\t{test_params["model_argv"]}\n")
    out_doc_header.AppendText(f"Q-FILE:\t{test_params["q_file_name"]}\n")
    out_doc_header.AppendText(f"LAW DOCS:\t{len(test_params["knowledge_files"])}\n")
    for file in test_params["knowledge_files"]:
        out_doc_header.AppendText(f"\t - {file}\n")
    out_doc_header.AppendText(f"\nPROMPT:{test_params["prompt_text"]}")
    out_doc_header.AppendText(f"\n{'#' * 40}\n")

    # get the response
    out_doc_p1 = section.AddParagraph()
    out_doc_p1.AppendText(response.get("result"))

    run_time_end: float = time.perf_counter() - run_time_start
    elapsed_time: str = time.strftime("%H:%M:%S", time.gmtime(run_time_end))
    out_doc_p1.AppendText(f"\n{'-' * 50}\n")
    out_doc_p1.AppendText(f"\tTotal Run Time:\t{elapsed_time}\n")
    out_doc.SaveToFile(rf"{test_params["output_file_path"]}\{ans_file_name}", FileFormat.Docx2019)
# def end

# ====  Function Definitions End =========================================================


def main() -> None:
    test_params: dict[str, Any] = setup()
    test_params["user_action"] = sys.argv[2]
    # -----------------------------------------------------------------------------------------------------
    start_time: float = 0.0
    end_time: float = 0.0

    input_tokens_total: float = 0.0
    input_tokens_total_price: float = 0.0

    output_tokens_total: float = 0.0
    output_tokens_total_price: float = 0.0

    answer_grand_total_price: float = 0.0
    grand_total_amount: float = 0.0

    input_tokens_rate: float = (
        consts.model_price_catalog[test_params["model_name_no_params"]][consts.INPUT_TOKENS_PRICE_1M] / consts.ONE_MILLION
    )
    output_tokens_rate: float = (
        consts.model_price_catalog[test_params["model_name_no_params"]][consts.OUTPUT_TOKENS_PRICE_1M] / consts.ONE_MILLION
    )
    # ------------------------------------------------------------------------------------------------------------
    # create the chain to answer questions
    qa_chain = RetrievalQA.from_chain_type(
        llm=test_params["llm_obj"],
        chain_type="stuff",
        retriever=dp.get_vector_db_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": test_params["prompt_template"]}
    )
    # ------------------------------------------------------------------------------------------------------------
    # list documents used to acquire the knowledge
    files: list[str] = os.listdir(dp.knowledge_docs_path)
    files = sorted([fi for fi in files if os.path.isfile(f"{dp.knowledge_docs_path}/{fi}")])
    test_params["knowledge_files"] = files

    # calculated number of tokens for the prompt
    prompt_tokens_num = prompts.calculate_tokens_num(test_params["llm_model"], test_params["prompt_template"])
    print(f"{prompt_tokens_num = }", end='\n\n')

    print(f"{'*' * 3} Started processing task(s)::{test_params["user_action"]}")
    try:
        match test_params["user_action"]:
            case "answer_law_questions":
                answer_law_questions(test_params, qa_chain)
            case "produce_court_claim":
                produce_court_claim(test_params, qa_chain)
            case _:
                print("Invalid / missing user action!")
                sys.exit(1)
    except Exception as err:
        print(err)
        sys.exit(1)
    print(f"{'*' * 3} Finished processing task(s) {'*' * 3}")



if __name__ == "__main__":
    main()
