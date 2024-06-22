from openai import OpenAI
import base64
import os
os.environ['OPENAI_API_KEY'] = "sk-proj-wGlurmBriyif87iiMWAMT3BlbkFJ1xhf2FL0Pgpknd0v1koU"


def describe_view(image_path):
    client = OpenAI()

    with open(image_path, "rb") as image_file:
        base64_img = base64.b64encode(image_file.read()).decode('utf-8')

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a visual assistant for a blind person. Please alert them of any obstacles and tell them where they should walk."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in front of me?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                    }
                ]
            }
        ],
        max_tokens=300
    )
    return completion.choices[0].message.content
