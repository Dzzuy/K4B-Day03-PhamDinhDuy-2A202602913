"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"
        self.used_fallback = False

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return (
            "[Mock Chatbot Response]: Tôi có thể giải thích quy trình HR chung, "
            "nhưng không có công cụ tra cứu hồ sơ cá nhân hoặc tạo đơn nghỉ phép."
        )

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        employee_match = re.search(r"\bvf\d{7}\b", prompt, re.IGNORECASE)
        employee_id = employee_match.group(0).upper() if employee_match else ""
        dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", prompt)

        if "[tool observation] submit_leave_request" in prompt_lower:
            status_match = re.search(r'"status":\s*"([^"]+)"', prompt)
            status = status_match.group(1) if status_match else ""
            request_match = re.search(r'"request_id":\s*"([^"]+)"', prompt)
            request_id = request_match.group(1) if request_match else ""
            message_matches = re.findall(r'"message":\s*"([^"]+)"', prompt)
            tool_message = message_matches[-1] if message_matches else "Yêu cầu nghỉ phép không thể hoàn tất."
            return {
                "type": "text",
                "content": (
                    f"Đã tạo đơn nghỉ phép {request_id}. Đơn đang chờ quản lý phê duyệt."
                    if status == "SUCCESS" and request_id else tool_message
                ),
                "thought": "Đã nhận kết quả từ tool tạo đơn và có thể trả lời người dùng."
            }

        if "[tool observation] employee_hr_query" in prompt_lower:
            if '"status": "not_found"' in prompt_lower:
                return {
                    "type": "text",
                    "content": f"Không tìm thấy nhân viên {employee_id}. Vui lòng kiểm tra lại mã nhân viên.",
                    "thought": "Tool không tìm thấy nhân viên nên tôi không được tự tạo dữ liệu."
                }

            if "tạo đơn" in prompt_lower and len(dates) >= 2:
                balance_match = re.search(r'"annual_leave_remaining":\s*(\d+)', prompt)
                remaining_days = int(balance_match.group(1)) if balance_match else 0
                start = datetime.strptime(dates[0], "%Y-%m-%d").date()
                end = datetime.strptime(dates[1], "%Y-%m-%d").date()
                requested_days = (end - start).days + 1
                if remaining_days < requested_days:
                    return {
                        "type": "text",
                        "content": (
                            f"Nhân viên {employee_id} chỉ còn {remaining_days} ngày phép, "
                            f"không đủ cho yêu cầu {requested_days} ngày nên tôi không tạo đơn."
                        ),
                        "thought": "Số ngày phép còn lại không đủ, dừng trước bước tạo đơn."
                    }
                return {
                    "type": "tool_call",
                    "tool_name": "submit_leave_request",
                    "arguments": {
                        "employee_id": employee_id,
                        "start_date": dates[0],
                        "end_date": dates[1],
                        "leave_type": "annual",
                        "reason": "Việc gia đình"
                    },
                    "thought": "Nhân viên còn đủ ngày phép, tiếp tục tạo đơn theo yêu cầu."
                }

            if '"query_type": "insurance_policy"' in prompt_lower:
                return {
                    "type": "text",
                    "content": (
                        f"Nhân viên {employee_id} đang tham gia gói bảo hiểm nhân viên tiêu chuẩn "
                        "(dữ liệu mô phỏng), gồm khám ngoại trú, điều trị nội trú và tai nạn lao động; "
                        "gói có hiệu lực đến 2026-12-31."
                    ),
                    "thought": "Đã nhận quyền lợi bảo hiểm từ tool và có thể tổng hợp câu trả lời."
                }

            balance_match = re.search(r'"annual_leave_remaining":\s*(\d+)', prompt)
            remaining_days = balance_match.group(1) if balance_match else "không xác định"
            return {
                "type": "text",
                "content": f"Nhân viên {employee_id} còn {remaining_days} ngày phép năm.",
                "thought": "Đã nhận số ngày phép từ tool và có thể trả lời người dùng."
            }

        if "bảo hiểm" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "employee_hr_query",
                "arguments": {"employee_id": employee_id, "query_type": "insurance_policy"},
                "thought": "Cần tra cứu quyền lợi bảo hiểm của nhân viên từ dữ liệu HR."
            }

        if "ngày phép" in prompt_lower or "phép còn lại" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "employee_hr_query",
                "arguments": {"employee_id": employee_id, "query_type": "leave_balance"},
                "thought": "Cần tra cứu số ngày phép còn lại trước khi trả lời hoặc tạo đơn."
            }

        if ("tạo đơn" in prompt_lower or "xin nghỉ" in prompt_lower) and len(dates) >= 2:
            leave_type = "sick" if "nghỉ ốm" in prompt_lower else "unpaid" if "không lương" in prompt_lower else "annual"
            reason_match = re.search(r"(?:lý do|vì)\s+(.+?)(?:\.|$)", prompt, re.IGNORECASE)
            return {
                "type": "tool_call",
                "tool_name": "submit_leave_request",
                "arguments": {
                    "employee_id": employee_id,
                    "start_date": dates[0],
                    "end_date": dates[1],
                    "leave_type": leave_type,
                    "reason": reason_match.group(1).strip() if reason_match else "Theo yêu cầu của nhân viên"
                },
                "thought": "Yêu cầu đã có đủ thông tin để tạo đơn nghỉ phép."
            }

        return {
            "type": "text",
            "content": (
                "[Mock Agent Response]: Nhân viên gửi đơn với thời gian, loại nghỉ và lý do. "
                "Đơn sau đó được chuyển cho quản lý xem xét."
            ),
            "thought": "Đây là câu hỏi HR chung nên không cần gọi tool."
        }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        self.used_fallback = False

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            self.used_fallback = True
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            self.used_fallback = True
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        self.used_fallback = False

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            self.used_fallback = True
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            self.used_fallback = True
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
