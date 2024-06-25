from openai import OpenAI
import base64


def describe_view(image_path):
    client = OpenAI()
    
    # get encoded version of image
    with open(image_path, "rb") as image_file:
        base64_img = base64.b64encode(image_file.read()).decode('utf-8')

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # system prompt to tell gpt it is an assistant
            {"role": "system", "content": "You are a visual assistant for a blind person. Please alert them of any obstacles and tell them where they should walk."},
            {
                "role": "user",
                # pose question and image for the robot to narrate
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
