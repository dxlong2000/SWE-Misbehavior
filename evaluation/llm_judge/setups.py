import re
import ast
import os 

from openai import OpenAI

from .prompts import build_prompt_IF


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)


def get_openrouter_answer(
        user_prompt, model="google/gemini-3-flash-preview", max_tokens=4096, 
        temperature=0.1, system_prompt="You are a helpful assistant!"):

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=max_tokens,
        temperature=temperature
    )

    return completion.choices[0].message.content


def extract_dictionary(text):
    pattern = r"<ANSWER>\s*(.*?)\s*</ANSWER>"
    result = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if result:
        dictionary = result.group(1)
        try:
            return ast.literal_eval(dictionary)
        except Exception:
            # print("Cannot parse the dictionary")
            raise ValueError("Cannot parse the dictionary")
    
    raise ValueError("Cannot find the dictionary")


def get_judge_IF(
    framework, task, task_desc, lessons, history_path,
    system_prompt, max_call=3, wait_for_callback=2,
    model="google/gemini-3-flash-preview", max_tokens=4096, temperature=0.1,
):
    import time
    prompt = build_prompt_IF(framework, task, task_desc, lessons, history_path)
    for attempt in range(max_call):
        try:
            response = get_openrouter_answer(
                prompt, model=model, max_tokens=max_tokens,
                temperature=temperature, system_prompt=system_prompt,
            )
            yes_no = re.search(r"<ANSWER>\s*(YES|NO)\s*</ANSWER>", response, re.IGNORECASE)
            if not yes_no:
                raise ValueError("No <ANSWER> tag found")
            meets = yes_no.group(1).upper() == "YES"
            return {"meets_spec": meets, "explain": response}
        except Exception as e:
            if attempt < max_call - 1:
                time.sleep(wait_for_callback)
            else:
                print(f"get_judge_IF failed after {max_call} attempts: {e}")
                return None

if __name__ == "__main__":
    print(get_openrouter_answer("Hello"))