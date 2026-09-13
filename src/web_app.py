"""FastAPI layer for the VinHR Agent Lab demo. Run: python src/web_app.py"""

import os
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import run_react_agent
from mcp_server import MCPHRServer
from prompts import CHATBOT_BASELINE_PROMPT
from providers import get_llm_provider
from tools import LEAVE_REQUESTS

ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"

app = FastAPI(title="VinHR Agent Lab", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")

EXAMPLES = [
    {"id": "general", "title": "Quy trình nghỉ phép", "tools": 0, "query": "Quy trình gửi đơn xin nghỉ phép thường gồm những bước nào?"},
    {"id": "leave", "title": "Tra cứu ngày phép", "tools": 1, "query": "Kiểm tra số ngày phép còn lại của nhân viên VF2026001."},
    {"id": "insurance", "title": "Tra cứu bảo hiểm", "tools": 1, "query": "Tra cứu thông tin bảo hiểm hiện tại của nhân viên VF2026001."},
    {"id": "leave-request", "title": "Tạo đơn hợp lệ", "tools": 1, "query": "Tạo đơn nghỉ cho VF2026001 từ 2026-10-05 đến 2026-10-06 vì việc gia đình."},
    {"id": "insufficient", "title": "Phép không đủ", "tools": 1, "query": "Tạo đơn nghỉ phép năm cho VF2026002 từ 2026-10-05 đến 2026-10-08 vì việc gia đình."},
    {"id": "not-found", "title": "Không tìm thấy nhân viên", "tools": 1, "query": "Tra cứu thông tin bảo hiểm của nhân viên VF9999999."},
    {"id": "multi-step", "title": "Kiểm tra rồi tạo đơn", "tools": 2, "query": "Kiểm tra ngày phép của VF2026001. Nếu còn ít nhất 3 ngày thì tạo đơn nghỉ phép năm từ 2026-10-13 đến 2026-10-15 vì việc gia đình."},
]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1500)
    mode: Literal["chatbot", "agent"] = "agent"
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)


def build_contextual_query(query: str, history: list[ChatMessage]) -> str:
    short_follow_up = len(query.split()) <= 4 and not any(char.isdigit() for char in query)
    recent_history = history[-2:] if short_follow_up else history[-12:]
    if not recent_history:
        return query
    lines = ["Lịch sử hội thoại gần nhất:"]
    for item in recent_history:
        speaker = "Người dùng" if item.role == "user" else "Trợ lý"
        lines.append(f"{speaker}: {item.content}")
    lines.append(f"Tin nhắn hiện tại của người dùng: {query}")
    lines.append("Hãy hiểu tin nhắn hiện tại dựa trên lịch sử nếu nó là câu trả lời ngắn hoặc thiếu thông tin.")
    return "\n".join(lines)


def provider_status(provider) -> dict:
    provider_name = provider.__class__.__name__
    configured = bool(getattr(provider, "is_configured", provider_name not in {"MockOfflineProvider"}))
    fallback = bool(getattr(provider, "used_fallback", False))
    return {
        "provider": provider_name,
        "model": getattr(provider, "model_name", "Offline-Mock-Model-2026"),
        "live_api": configured and not fallback and provider_name != "MockOfflineProvider",
        "fallback": fallback or provider_name == "MockOfflineProvider",
        "warning": getattr(provider, "fallback_reason", "") if fallback else ""
    }


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "vinhr-agent-lab"}


@app.get("/api/status")
def status():
    return provider_status(get_llm_provider())


@app.get("/api/examples")
def examples():
    return {"examples": EXAMPLES}


@app.get("/api/tools")
def tools():
    return {"server": "vinfast_hr_mcp", "tools": MCPHRServer().list_tools(), "data_label": "Dữ liệu demo mô phỏng"}


@app.get("/api/leave-requests")
def leave_requests():
    return {"requests": LEAVE_REQUESTS, "data_label": "Đơn nghỉ demo mô phỏng"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Vui lòng nhập câu hỏi HR.")

    provider = get_llm_provider()
    contextual_query = build_contextual_query(query, request.history)
    if request.mode == "chatbot":
        answer = await run_in_threadpool(provider.generate, contextual_query, CHATBOT_BASELINE_PROMPT)
        return {"answer": answer, "mode": "chatbot", "trace": [], **provider_status(provider)}

    mcp_server = MCPHRServer()
    trace = await run_in_threadpool(run_react_agent, contextual_query, provider, mcp_server)
    answer = next((event.get("output", "") for event in reversed(trace) if event.get("action_type") == "FINAL_ANSWER"), "Agent chưa tạo được câu trả lời cuối cùng.")
    return {"answer": answer, "mode": "agent", "trace": trace, **provider_status(provider)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=False)
