"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from datetime import datetime
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "employee_hr_query",
        "description": (
            "Tra cứu ngày phép còn lại hoặc quyền lợi bảo hiểm hiện tại của một "
            "nhân viên bằng mã nhân viên. Đây là tool chỉ đọc dữ liệu."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên cần tra cứu (ví dụ: 'VF2026001')"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["leave_balance", "insurance_policy"],
                    "description": (
                        "Loại thông tin cần tra cứu: 'leave_balance' cho ngày phép "
                        "còn lại hoặc 'insurance_policy' cho quyền lợi bảo hiểm."
                    )
                }
            },
            "required": ["employee_id", "query_type"]
        }
    },
    {
        "name": "submit_leave_request",
        "description": (
            "Tạo đơn xin nghỉ phép cho nhân viên. Chỉ gọi khi đã có đủ mã nhân viên, "
            "ngày bắt đầu, ngày kết thúc, loại nghỉ và lý do."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên tạo đơn (ví dụ: 'VF2026001')"
                },
                "start_date": {
                    "type": "string",
                    "description": "Ngày bắt đầu nghỉ theo định dạng YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "Ngày kết thúc nghỉ theo định dạng YYYY-MM-DD"
                },
                "leave_type": {
                    "type": "string",
                    "enum": ["annual", "sick", "unpaid"],
                    "description": "Loại nghỉ: phép năm, nghỉ ốm hoặc nghỉ không lương"
                },
                "reason": {
                    "type": "string",
                    "description": "Lý do xin nghỉ, viết ngắn gọn và rõ ràng"
                }
            },
            "required": ["employee_id", "start_date", "end_date", "leave_type", "reason"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_EMPLOYEE_DATABASE = {
    "VF2026001": {
        "full_name": "Nguyễn Văn An",
        "department": "Phân tích dữ liệu",
        "position": "Data Analyst",
        "annual_leave_remaining": 10,
        "insurance": {
            "plan_name": "Gói bảo hiểm nhân viên tiêu chuẩn (mô phỏng)",
            "enrollment_status": "Đang tham gia",
            "coverage": ["Khám ngoại trú", "Điều trị nội trú", "Tai nạn lao động"],
            "valid_until": "2026-12-31"
        }
    },
    "VF2026002": {
        "full_name": "Trần Thị Bình",
        "department": "Vận hành",
        "position": "Operations Specialist",
        "annual_leave_remaining": 2,
        "insurance": {
            "plan_name": "Gói bảo hiểm nhân viên tiêu chuẩn (mô phỏng)",
            "enrollment_status": "Đang tham gia",
            "coverage": ["Điều trị nội trú", "Tai nạn lao động"],
            "valid_until": "2026-12-31"
        }
    }
}

LEAVE_REQUESTS = []


def execute_employee_hr_query(employee_id: str, query_type: str) -> str:
    """Tra cứu ngày phép hoặc quyền lợi bảo hiểm từ dữ liệu HR mô phỏng."""
    normalized_id = employee_id.strip().upper()
    employee = MOCK_EMPLOYEE_DATABASE.get(normalized_id)

    if not employee:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy nhân viên có mã '{normalized_id}'. Hãy kiểm tra lại mã nhân viên."
        }, ensure_ascii=False)

    if query_type == "leave_balance":
        data = {
            "full_name": employee["full_name"],
            "department": employee["department"],
            "annual_leave_remaining": employee["annual_leave_remaining"]
        }
    elif query_type == "insurance_policy":
        data = {
            "full_name": employee["full_name"],
            "department": employee["department"],
            "insurance": employee["insurance"]
        }
    else:
        return json.dumps({
            "status": "INVALID_ARGUMENT",
            "message": "query_type chỉ nhận 'leave_balance' hoặc 'insurance_policy'."
        }, ensure_ascii=False)

    return json.dumps({
        "status": "SUCCESS",
        "employee_id": normalized_id,
        "query_type": query_type,
        "data": data
    }, ensure_ascii=False)


def execute_submit_leave_request(
    employee_id: str,
    start_date: str,
    end_date: str,
    leave_type: str,
    reason: str
) -> str:
    """Tạo đơn nghỉ phép sau khi kiểm tra mã nhân viên, ngày và số phép còn lại."""
    normalized_id = employee_id.strip().upper()
    employee = MOCK_EMPLOYEE_DATABASE.get(normalized_id)

    if not employee:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy nhân viên có mã '{normalized_id}'. Không thể tạo đơn."
        }, ensure_ascii=False)

    if leave_type not in {"annual", "sick", "unpaid"}:
        return json.dumps({
            "status": "INVALID_ARGUMENT",
            "message": "leave_type chỉ nhận 'annual', 'sick' hoặc 'unpaid'."
        }, ensure_ascii=False)

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return json.dumps({
            "status": "INVALID_ARGUMENT",
            "message": "Ngày phải có định dạng YYYY-MM-DD, ví dụ 2026-09-21."
        }, ensure_ascii=False)

    if start > end:
        return json.dumps({
            "status": "INVALID_ARGUMENT",
            "message": "Ngày bắt đầu không được sau ngày kết thúc."
        }, ensure_ascii=False)

    requested_days = (end - start).days + 1
    remaining_days = employee["annual_leave_remaining"]
    if leave_type == "annual" and requested_days > remaining_days:
        return json.dumps({
            "status": "INSUFFICIENT_LEAVE",
            "requested_days": requested_days,
            "remaining_days": remaining_days,
            "message": "Số ngày xin nghỉ vượt quá số ngày phép năm còn lại."
        }, ensure_ascii=False)

    request_id = f"LR-{normalized_id}-{len(LEAVE_REQUESTS) + 1:03d}"
    request = {
        "request_id": request_id,
        "employee_id": normalized_id,
        "start_date": start_date,
        "end_date": end_date,
        "requested_days": requested_days,
        "leave_type": leave_type,
        "reason": reason.strip(),
        "approval_status": "PENDING"
    }
    LEAVE_REQUESTS.append(request)

    return json.dumps({
        "status": "SUCCESS",
        **request,
        "remaining_days_before_approval": remaining_days,
        "message": f"Đã tạo đơn {request_id}. Đơn đang chờ quản lý phê duyệt."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "employee_hr_query": execute_employee_hr_query,
    "submit_leave_request": execute_submit_leave_request
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
