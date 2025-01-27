import src.prompts as pmpt
# from enum import Enum

# from pydantic import BaseModel

WIN_ENCODING_RU: str = "Windows-1251"


class LLM_Model(object):
    def __init__(self, name: str, encoding: str, price: float):
        self.name = name
        self.token_price = price
        self.encoding = encoding
# class LLM_Model end

# ----------------------------------------------------------------
GPT_4o1_MINI: str = "o1-mini"
GPT_4o_MINI: str = "gpt-4o-mini"

AI_MODELS: dict[str, str] = {
    GPT_4o1_MINI: "o1-mini",
    "gpt-4o1-preview": "o1-preview",
    "gpt-4o": "gpt-4o-2024-08-06",
    GPT_4o_MINI: "gpt-4o-mini",
    "gpt-4": "gpt-4-32k",
    "gpt-3-turbo": "gpt-3.5-turbo-16k"
}

# ----------------------------------------------------------------
INPUT_TOKENS_PRICE_1K: str = "input_tokens_price_1k"
CACHED_INPUT_TOKENS_PRICE_1K: str = "1k_cached_input_tokens_price"
OUTPUT_TOKENS_PRICE_1K: str = "output_tokens_price_1k"
# ----------------------------------------------------------------
model_price_catalog: dict[str, dict[str, any]] = {
    GPT_4o1_MINI: {
        INPUT_TOKENS_PRICE_1K: 0.003,
        CACHED_INPUT_TOKENS_PRICE_1K: 0.0015,
        OUTPUT_TOKENS_PRICE_1K: 0.012,
    },
    "gpt-o1-preview": {
        INPUT_TOKENS_PRICE_1K: 0.015,
        CACHED_INPUT_TOKENS_PRICE_1K: 0.0075,
        OUTPUT_TOKENS_PRICE_1K: 0.06,
    },
    "gpt-o1": {
        INPUT_TOKENS_PRICE_1K: 0.015,
        CACHED_INPUT_TOKENS_PRICE_1K: 0.0075,
        OUTPUT_TOKENS_PRICE_1K: 0.06,
    },
    GPT_4o_MINI: {
        INPUT_TOKENS_PRICE_1K: 0.00015,
        CACHED_INPUT_TOKENS_PRICE_1K: 0.000075,
        OUTPUT_TOKENS_PRICE_1K: 0.0006,
    },
    "gpt-4o": {
        INPUT_TOKENS_PRICE_1K: 0.0025,
        CACHED_INPUT_TOKENS_PRICE_1K: 0.00125,
        OUTPUT_TOKENS_PRICE_1K: 0.01,
    }
}


topic_2_prompt_mapping: dict[str, str] = {
    "question_prompt": pmpt.sys_prompt_to_answer_question_ru,
    "penalty_prompt": pmpt.sys_prompt_to_calculate_penalty_ru
}

