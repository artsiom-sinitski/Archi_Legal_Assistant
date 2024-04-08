import os
import json

# from pathlib import Path
from archi.src.constants import WIN_ENCODING_RU


# --- PATH SETTINGS ---
# current_dir: Path = Path(__file__).parent if "__file__" in locals() else Path.cwd()


def main() -> None:
    file_path = rf"{os.environ["USERDIR"]}\Documents\archi_knowledge_docs\test_q_and_a"
    file_name = "Test_questions_20240327.json"
    data, questions = None, None

    with open(fr"{file_path}\{file_name}", encoding=WIN_ENCODING_RU) as fp:
        data = json.load(fp)

    questions = data.get("Questions")
    # pprint(questions)

    for question in questions:
        print(question)


if __name__ == "__main__":
    main()
