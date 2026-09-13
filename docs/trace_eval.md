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

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Kiểm thử Offline Mock đã chạy 5/5. Đã thử Gemini API thật: TC01, TC02, TC03 và bước tra cứu đầu của TC04 chạy bằng Gemini, nhưng free-tier chặn các lượt sau vì giới hạn 5 request/phút. Tôi sẽ chạy lại bộ test sau khi quota hồi và chỉ dùng trace có `live_api: true` cho bài nộp.

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "query": "Kiểm tra ngày phép của VF2026001. Nếu còn ít nhất 3 ngày thì tạo đơn nghỉ phép năm từ 2026-09-21 đến 2026-09-23 vì việc gia đình.",
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
    "latency_ms": 0.01
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ ] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI). *(Đã có key; đã chạy một phần nhưng chưa đạt 5/5 vì quota.)*
- **Kết quả kiểm thử Offline Mock:** 5 / 5 test cases.
- **Tổng số Test Cases chạy bằng API thật:** ___ / 5 test cases.
- **Số lượt gọi Tool qua MCP Server trong lần chạy Mock:** 5 lượt.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
