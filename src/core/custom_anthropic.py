from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_anthropic.output_parsers import extract_tool_calls
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration


# extend ChatAnthropic to skip token calculation as I'm using a proxy to access the api.
class CustomChatAnthropic(ChatAnthropic):
    def _format_output(self, data: Any, **kwargs: Any) -> ChatResult:
        """override this method to skip token calculation """

        data_dict = data.model_dump()
        content = data_dict["content"]
        llm_output = {
            k: v for k, v in data_dict.items() if k not in ("content", "role", "type")
        }
        if len(content) == 1 and content[0]["type"] == "text":
            msg = AIMessage(content=content[0]["text"])
        elif any(block["type"] == "tool_use" for block in content):
            tool_calls = extract_tool_calls(content)
            msg = AIMessage(
                content=content,
                tool_calls=tool_calls,
            )
        else:
            msg = AIMessage(content=content)
        # setup all usage fields to None
        msg.usage_metadata = {
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None
        }
        return ChatResult(
            generations=[ChatGeneration(message=msg)],
            llm_output=llm_output,
        )
