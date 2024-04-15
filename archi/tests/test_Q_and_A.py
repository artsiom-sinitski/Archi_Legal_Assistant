import os
import json
from pprint import pprint
from datetime import datetime

# from pathlib import Path
from archi.src.constants import WIN_ENCODING_RU
from archi.src.prompts import sys_prompt_en_1
from archi.src import docs_processor as dp


# --- PATH SETTINGS ---
# current_dir: Path = Path(__file__).parent if "__file__" in locals() else Path.cwd()


def main() -> None:
    curr_date = datetime.now()

    file_path = rf"{os.environ["USERDIR"]}\Documents\archi_knowledge_docs\test_q_and_a"
    # ---------------------------------------------------------------------------------
    # questions_file_name = "Consumer_protection_law-25_questions.json"
    questions_file_name = "Retail_Sale_Law-20_questions.json"
    topic = questions_file_name.split('-')[0]
    ans_file_name = f"Answers_to_{topic}_{curr_date.strftime("%Y%m%d")}.txt"
    # ---------------------------------------------------------------------------------

    data, questions = None, None

    with open(fr"{file_path}\{questions_file_name}", 'r', encoding=WIN_ENCODING_RU) as fp:
        data = json.load(fp)

    questions = data.get("Questions")
    # pprint(questions)

    with open(fr"{file_path}\{ans_file_name}", 'w', encoding=WIN_ENCODING_RU) as fp:
        fp.write(f"Date:\t{curr_date.strftime("%Y-%m-%d %H:%M")}\n")
        fp.write(f"Encoding:\t{WIN_ENCODING_RU}\n\n")
        fp.write(f"PROMPT:{sys_prompt_en_1}")
        fp.write(f"\n{'#'*70}\n")

        for idx, question in enumerate(questions, start=1):
            fp.writelines([f"Q{idx}:\n", f"{question}\n\n", "Answer:\n"])
            # pprint(dp.qa_chain(question))
            answer = dp.qa_chain(question)
            fp.write(answer.get("result"))
            # fp.write(answer.get("source_documents"))
            fp.write(f"\n {'-'*70} \n")
            print(f"Processed -> {idx}. {question}")
        # for end
    # with end


if __name__ == "__main__":
    main()
