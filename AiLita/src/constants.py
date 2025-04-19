import src.prompts as pmpt

# from pydantic import BaseModel

WIN_ENCODING_RU: str = "Windows-1251"

# ----------------------------------------------------------------
class LLM_Model(object):
    def __init__(self, name: str, encoding: str, price: float):
        self.name = name
        self.token_price = price
        self.encoding = encoding
# class LLM_Model end

# ----------------------------------------------------------------
DEEPSEEK_R1: str = "deepseek-r1"

GPT_4o3_MINI: str = "o3-mini"
GPT_4o3_MINI_HIGH: str = "o3-mini-high"

GPT_4o1: str = "o1"
GPT_4o1_MINI: str = "o1-mini"

GPT_4o: str = "gpt-4o"
GPT_4o_MINI: str = "gpt-4o-mini"

AI_MODELS: dict[str, str] = {
    DEEPSEEK_R1: "deepseek-reasoner",
    GPT_4o3_MINI_HIGH: "o3-mini-high",
    GPT_4o3_MINI: "o3-mini",
    GPT_4o1_MINI: "o1-mini",
    "gpt-4o": "gpt-4o-2024-08-06",
    GPT_4o_MINI: "gpt-4o-mini",
    "gpt-4": "gpt-4-32k",
    "gpt-3-turbo": "gpt-3.5-turbo-16k"
}

# ----------------------------------------------------------------
ONE_MILLION: int = 1_000_000
INPUT_TOKENS_PRICE_1M: str = "input_tokens_price_1m"
CACHED_INPUT_TOKENS_PRICE_1M: str = "cached_input_tokens_price_1m"
OUTPUT_TOKENS_PRICE_1M: str = "output_tokens_price_1m"
# ----------------------------------------------------------------
# prices are per 1 million tokens in USD ($)
model_price_catalog: dict[str, dict[str, float]] = {
    DEEPSEEK_R1: {
        INPUT_TOKENS_PRICE_1M: 0.55,
        CACHED_INPUT_TOKENS_PRICE_1M: 0.14,
        OUTPUT_TOKENS_PRICE_1M: 2.19,
    },
    GPT_4o3_MINI_HIGH: {
        INPUT_TOKENS_PRICE_1M: 1.1,
        CACHED_INPUT_TOKENS_PRICE_1M: 0.55,
        OUTPUT_TOKENS_PRICE_1M: 4.4,
    },
    GPT_4o3_MINI: {
        INPUT_TOKENS_PRICE_1M: 1.1,
        CACHED_INPUT_TOKENS_PRICE_1M: 0.55,
        OUTPUT_TOKENS_PRICE_1M: 4.4,
    },
    GPT_4o1_MINI: {
        INPUT_TOKENS_PRICE_1M: 1.1,
        CACHED_INPUT_TOKENS_PRICE_1M: 0.55,
        OUTPUT_TOKENS_PRICE_1M: 4.4,
    },
    GPT_4o1: {
        INPUT_TOKENS_PRICE_1M: 15,
        CACHED_INPUT_TOKENS_PRICE_1M: 7.5,
        OUTPUT_TOKENS_PRICE_1M: 60,
    },
    GPT_4o_MINI: {
        INPUT_TOKENS_PRICE_1M: 0.15,
        CACHED_INPUT_TOKENS_PRICE_1M: 0.075,
        OUTPUT_TOKENS_PRICE_1M: 0.6,
    },
    GPT_4o: {
        INPUT_TOKENS_PRICE_1M: 2.5,
        CACHED_INPUT_TOKENS_PRICE_1M: 1.25,
        OUTPUT_TOKENS_PRICE_1M: 10,
    }
}


topic_2_prompt_mapping: dict[str, str] = {
    "question_prompt": pmpt.sys_prompt_to_answer_question_ru,
    "penalty_prompt": pmpt.sys_prompt_to_calculate_penalty_ru
}

