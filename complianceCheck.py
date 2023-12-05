#python 3

def complianceCheck(file_content):
    #Note: The openai-python library support for Azure OpenAI is in preview.
    #Note: This code sample requires OpenAI Python library version 0.28.1 or lower.
    import os
    import openai

    openai.api_type = "azure"
    openai.api_base = "https://84c98458-83a5-4d5e-9cdd-e1b0a12b07f4-canadaeast.openai.azure.com/"
    openai.api_version = "2023-07-01-preview"
    openai.api_key = "333ee4ac595d44978d37e81b2eb063c2"

    message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content": file_content}]

    completion = openai.ChatCompletion.create(
    engine="gpt-35-turbo",
    messages = message_text,
    temperature=0.7,
    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
    )

    return completion


import openai
import glob

files = glob.glob("**/*yaml")

s = ""
for f in files:
    file_content = ""
    with open(f) as fp:
        file_content = fp.read()

    if file_content == "":
        continue
    out = complianceCheck(file_content)

    s += out["choices"][0]["message"]["content"]

print(f'::set-output name=result::{s}')


