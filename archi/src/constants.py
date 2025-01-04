import src.prompts as pmpt


WIN_ENCODING_RU: str = "Windows-1251"


AI_MODELS: dict[str, str] = {
    "gpt-4o1-mini": "o1-mini",
    "gpt-4o1-preview": "o1-preview",
    "gpt-4o": "gpt-4o-2024-08-06",
    "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
    "gpt-4": "gpt-4-32k",
    "gpt3-turbo": "gpt-3.5-turbo-16k"
}


topic_2_prompt_mapping: dict[str, str] = {
    "question_prompt": pmpt.sys_prompt_to_answer_question_ru,
    "penalty_prompt": pmpt.sys_prompt_to_calculate_penalty_ru
}

