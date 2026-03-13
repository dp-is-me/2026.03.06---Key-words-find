import json
import os
from typing import Any, Dict

from openai import OpenAI


SYSTEM_PROMPT = """
You are a real-time senior network engineer assistant.
Analyze screenshots from live troubleshooting sessions (MS Teams, terminal, dashboards).
You must:
1) Infer the likely network toolset/vendor in use (Cisco/Fortinet/Palo Alto/other).
2) Produce concise, actionable troubleshooting recommendations.
3) Prioritize only ONE immediate next action first.
4) Keep a queue of follow-up actions ordered by priority.
5) Avoid repeating actions that were already attempted and failed.
6) Focus on safe, reversible checks before disruptive changes.
Return strict JSON with this schema:
{
  "toolset": "string",
  "summary": "string",
  "recommended_action": "string",
  "follow_up_actions": ["string", "string"],
  "confidence": "low|medium|high"
}
"""


class NetworkExpertAgent:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def analyze_frame(self, frame_b64: str, context: Dict[str, Any]) -> Dict[str, Any]:
        context_text = json.dumps(context, indent=2)

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Here is recent troubleshooting context. Do not repeat failed attempts.\n"
                                f"{context_text}\n"
                                "Analyze this frame and provide the next best recommendation."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{frame_b64}",
                        },
                    ],
                },
            ],
            text={"format": {"type": "json_object"}},
            max_output_tokens=600,
        )

        raw = response.output_text
        parsed = json.loads(raw)
        parsed.setdefault("follow_up_actions", [])
        return parsed
