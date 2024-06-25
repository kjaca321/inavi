from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "turn_robot",
            "description": "Turn the robot to face a given direction",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "The way the robot should face, e.g. left, right, around",
                        "enum": ["left", "right", "around"]
                    },
                },
                "required": ["direction"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_ahead",
            "description": "Move the robot in the forward / ahead direction, optionally with distance and unit",
            "parameters": {
                "type": "object",
                "properties": {
                    "distance": {
                        "type": "number",
                        "description": "A number detailing how far forward the robot should move",
                    },
                    "units": {
                        "type": "string",
                        "description": "What unit the distance given is in, feet or meters",
                        "enum": ["feet", "meters"]
                    }
                },
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_view",
            "description": "Tell the user what the camera sees"
        }
    }
]


def choose_function(user_request):
    client = OpenAI()
    # ask gpt to choose from the above tools based on the user's input
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_request}],
        tools=TOOLS
    )
    return response.choices[0].message.tool_calls[0].function
