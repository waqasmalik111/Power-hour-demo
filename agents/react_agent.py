import os
import json
import urllib.request
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# ---------- Core types ----------
class StepType(Enum):
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    ANSWER = "answer"

@dataclass
class Step:
    type: StepType
    content: str

class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    def execute(self, *args, **kwargs) -> str:
        raise NotImplementedError

# ---------- Prompts for codegen ----------
CODEGEN_SYSTEM_PROMPT = (
    "You are an expert software engineer. "
    "Generate high-quality, production-ready code that satisfies the user's requirements. "
    "Return ONLY code unless explicitly asked for explanation. Use clear names and docstrings when helpful."
)

CODEGEN_USER_PROMPT = """Generate code with the following requirements.

Language: {language}

Task:
{task}

Return the complete code implementation.
"""

# ---------- LLM client (OpenAI/Mistral-compatible) ----------
class MistralLLMClient:
    """
    Generic client for OpenAI-style /v1/chat/completions endpoints.
    Configure via env:
      API_BASE_URL (default: your RHOAI gateway)
      API_KEY      (required)
      MODEL_NAME   (default: mistral-small-24b-w8a8)
    """
    def __init__(self):
        self.base_url = os.getenv(
            "API_BASE_URL",
            "https://mistral-small-24b-w8a8-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
        ).rstrip("/")
        self.api_key  = os.getenv("API_KEY", "")
        self.model    = os.getenv("MODEL_NAME", "mistral-small-24b-w8a8")

    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 800) -> str:
        if not self.api_key:
            raise RuntimeError("API_KEY is not set")
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return (
                    result.get("choices", [{}])[0]
                          .get("message", {})
                          .get("content", "")
                          .strip()
                )
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return ""

# ---------- Code Generation tool ----------
class CodeGenTool(Tool):
    def __init__(self):
        super().__init__(name="code_gen_tool", description="Generate python code for the given task.")
        self.llm_client = MistralLLMClient()

    def execute(self, task: str = "") -> str:
        messages = [
            {"role": "system", "content": CODEGEN_SYSTEM_PROMPT},
            {"role": "user", "content": CODEGEN_USER_PROMPT.format(language="python", task=task)},
        ]
        return self.llm_client.chat_completion(messages) or "Error calling code gen"

# ---------- Code Validation tool ----------
VALIDATE_SYSTEM_PROMPT = (
    "You are a senior code reviewer. Validate the submitted code for correctness, "
    "readability, edge cases, performance, security, and style. "
    "Respond with a concise review including:\n"
    "- Summary verdict (Pass/Needs changes)\n"
    "- Issues (with line refs if possible)\n"
    "- Security concerns\n"
    "- Suggested fixes (patch-style or exact snippets)\n"
    "- Tests to add\n"
)

VALIDATE_USER_PROMPT = """Validate the following code.

Language: {language}

Guidelines (optional):
{guidelines}
Code:
```
{code}
```
"""
class CodeValidateTool(Tool):
    def __init__(self):
        super().__init__(name="code_validate_tool", description="Validate code for bugs, security, style, and tests.")
        self.llm_client = MistralLLMClient()

    def execute(self, code: str = "", language: str = "python", guidelines: str = "") -> str:
        if not code.strip():
            return "Error: no code provided for validation."
        messages = [
            {"role": "system", "content": VALIDATE_SYSTEM_PROMPT},
            {"role": "user", "content": VALIDATE_USER_PROMPT.format(
                language=language,
                guidelines=guidelines or "N/A",
                code=code
            )},
        ]
        return self.llm_client.chat_completion(messages, temperature=0.2, max_tokens=1200) or "Error calling code validation"

# ---------- ReAct agent ----------
class ReActAgent:
    """
    Minimal agent: chooses between code generation and code validation.
    Expects run(query | payload) -> {'answer': str, 'history': [...]}
    """
    def __init__(self, tools: List[Tool], llm_client=None, max_steps: int = 3, verbose: bool = False):
        self.tools = {t.name: t for t in tools}
        self.verbose = verbose
        self.history: List[Step] = []
        self.llm_client = llm_client

    def _use_tool(self, tool_name: str, *args, **kwargs) -> str:
        tool = self.tools.get(tool_name)
        if not tool:
            obs = f"Error: {tool_name} not available"
            self.history.append(Step(StepType.OBSERVATION, obs))
            return obs
        out = tool.execute(*args, **kwargs)
        self.history.append(Step(StepType.OBSERVATION, out))
        return out

    def run(self, query: Any) -> Dict[str, Any]:
        # Decide mode
        mode = "generate"

        if isinstance(query, dict) and query.get("mode") == "validate":
            mode = "validate"
        elif isinstance(query, str):
            qlow = query.lower()
            if qlow.startswith("validate:") or qlow.startswith("review:") or "```" in qlow:
                mode = "validate"

        if mode == "validate":
            self.history.append(Step(StepType.THOUGHT, "I should validate the provided code."))
            self.history.append(Step(StepType.ACTION, "code_validate_tool[...]"))

            if isinstance(query, dict):
                code = query.get("code", "")
                language = query.get("language", "python")
                guidelines = query.get("guidelines", "")
            else:
                code = query
                language = "python"
                guidelines = ""

            answer = self._use_tool("code_validate_tool", code=code, language=language, guidelines=guidelines)

        else:
            self.history.append(Step(StepType.THOUGHT, "I should generate code for the user's request."))
            self.history.append(Step(StepType.ACTION, "code_gen_tool[...]"))
            answer = self._use_tool("code_gen_tool", query)

        self.history.append(Step(StepType.ANSWER, answer))
        return {"answer": answer, "history": self.get_history_dict()}

    def get_history_dict(self) -> List[Dict[str, str]]:
        return [{"type": s.type.value, "content": s.content} for s in self.history]

    def reset(self):
        self.history = []

