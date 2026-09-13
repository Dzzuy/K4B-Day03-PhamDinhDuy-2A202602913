# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Phạm Đình Duy
>
> **Mã Sinh Viên / Mã Học viên:** 2A202602913
>
> **Chủ đề Lựa chọn:** Trợ lý Nhân sự VinFast (HR Assistant)

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Với yêu cầu có điều kiện, Agent phải tra cứu ngày phép, so sánh số ngày rồi mới quyết định có tạo đơn hay không. |
| **2. Tool Interaction** | 5 / 5 | Agent cần gọi MCP Server để đọc ngày phép, quyền lợi bảo hiểm và gửi đơn nghỉ phép. Chatbot thường không tự làm được các việc này. |
| **3. Dynamic Decision** | 5 / 5 | Bước tạo đơn phụ thuộc trực tiếp vào Observation về số ngày phép còn lại. Nếu không đủ phép thì Agent phải dừng. |
| **4. Long Horizon Goal** | 3 / 5 | Agent phải giữ mục tiêu qua vài bước tra cứu và tạo đơn, nhưng quy trình vẫn ngắn và không kéo dài qua nhiều phiên. |
| **TỔNG ĐIỂM AGENTIC FIT** | **17 / 20** | Bài toán đạt trên 12/20 nên phù hợp để triển khai Agentic System. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

Đã chạy đủ 5/5 test cases bằng ShopAI live API qua lệnh:

```bash
python src/app.py --all
```

Kết quả terminal xác nhận:

```text
Đã thực thi 5/5 Test Cases | 0 Test Cases đang chờ điền câu hỏi (TODO)
[API MODE]: Toàn bộ lượt gọi LLM đã dùng API thật.
```

File trace đầy đủ đã được lưu tại `docs/trace_waterfall.json`. Trace có 10 sự kiện, gồm 5 `TOOL_EXECUTION` / 5 `FINAL_ANSWER`, tất cả đều có `"live_api": true`.

Ví dụ đoạn trace quan trọng nhất ở TC04, Agent phải tra cứu phép trước rồi mới tạo đơn:

```json
[
  {
    "step": 1,
    "query": "Kiểm tra ngày phép của VF2026001. Nếu còn ít nhất 3 ngày thì tạo đơn nghỉ phép năm từ 2026-09-21 đến 2026-09-23 vì việc gia đình.",
    "action_type": "TOOL_EXECUTION",
    "thought": "ShopAIKey quyết định gọi công cụ 'employee_hr_query'.",
    "tool_name": "employee_hr_query",
    "arguments": {
      "employee_id": "VF2026001",
      "query_type": "leave_balance"
    },
    "observation": {
      "status": "SUCCESS",
      "employee_id": "VF2026001",
      "query_type": "leave_balance",
      "data": {
        "full_name": "Nguyễn Văn An",
        "department": "Phân tích dữ liệu",
        "annual_leave_remaining": 10
      }
    },
    "llm_provider": "ShopAIProvider",
    "live_api": true
  },
  {
    "step": 2,
    "query": "Kiểm tra ngày phép của VF2026001. Nếu còn ít nhất 3 ngày thì tạo đơn nghỉ phép năm từ 2026-09-21 đến 2026-09-23 vì việc gia đình.",
    "action_type": "TOOL_EXECUTION",
    "thought": "ShopAIKey quyết định gọi công cụ 'submit_leave_request'.",
    "tool_name": "submit_leave_request",
    "arguments": {
      "employee_id": "VF2026001",
      "start_date": "2026-09-21",
      "end_date": "2026-09-23",
      "leave_type": "annual",
      "reason": "việc gia đình"
    },
    "observation": {
      "status": "SUCCESS",
      "request_id": "LR-VF2026001-001",
      "approval_status": "PENDING"
    },
    "llm_provider": "ShopAIProvider",
    "live_api": true
  },
  {
    "step": 3,
    "query": "Kiểm tra ngày phép của VF2026001. Nếu còn ít nhất 3 ngày thì tạo đơn nghỉ phép năm từ 2026-09-21 đến 2026-09-23 vì việc gia đình.",
    "action_type": "FINAL_ANSWER",
    "output": "Đã tạo đơn xin nghỉ phép năm cho mã nhân viên VF2026001 từ 2026-09-21 đến 2026-09-23 vì việc gia đình. Mã đơn là LR-VF2026001-001 và đang chờ quản lý phê duyệt.",
    "llm_provider": "ShopAIProvider",
    "live_api": true
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã cấu hình provider live API trong `.env` và xác nhận Agent chạy thành công bằng ShopAI API thật.
- **Kết quả kiểm thử Offline Mock:** 5 / 5 test cases.
- **Tổng số Test Cases chạy bằng API thật:** 5 / 5 test cases.
- **Số sự kiện trong Waterfall Trace:** 10 sự kiện.
- **Số lượt gọi Tool qua MCP Server trong lần chạy API thật:** 5 lượt.
- **LLM Provider nghiệm thu:** ShopAIProvider.
- **Kết quả đẩy Repo nộp bài:** [ ] Chờ commit và push bản cuối lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
