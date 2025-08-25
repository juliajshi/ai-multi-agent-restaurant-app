from langchain_core.output_parsers import PydanticOutputParser
from typing import Dict


def parse_structured_output(result: Dict, parser: PydanticOutputParser):
    try:
        raw_output = result.get("output")
        output_text = raw_output[0]["text"]
        # Handle both possible response structures
        if (
            isinstance(raw_output, list)
            and len(raw_output) > 0
            and "text" in raw_output[0]
        ):
            # Structure: [{'text': '...', 'type': 'text', 'index': 0}]
            output_text = raw_output[0]["text"]
            # ["top_recommendations"]
        elif isinstance(raw_output, str):
            # Structure: direct string
            output_text = raw_output
        else:
            # Fallback
            output_text = str(raw_output)

        return parser.parse(output_text)

    except Exception as e:
        print(f"Could not parse structured output: {e}")
        return None
