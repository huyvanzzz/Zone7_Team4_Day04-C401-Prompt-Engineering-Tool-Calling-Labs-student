# Day 04 Lab v2 Report - Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A - Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B - Chi tiết / Bằng chứng**: bảng đầy đủ (v0-v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Zone7 Team 4
- Members: Trần Quốc Khánh - 2A202600679, Nguyễn Văn Huy - 2A202600773, Nguyễn Anh Kiệt - 2A202600677
- Provider/model: OpenAI-compatible gateway via `.env` (`OPENAI_MODEL` currently set in the local environment)

---

# PHẦN A - Giới thiệu agent

## A1. Agent này làm được gì

Research agent của nhóm dùng để tìm tin theo từ khóa hoặc account X/Twitter, đọc URL, tổng hợp thành digest, đánh giá nguồn, tra policy/paper, và gửi nội dung lên Telegram khi đã được xác nhận. Agent được build để trả lời ngắn gọn, đúng tool, và ưu tiên bằng chứng hơn là đoán.

**Link dùng thử (deploy):**

> URL:  https://35v3gcmv-8501.asse.devtunnels.ms/

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận | không |
| timeline | Lấy bài đăng gần đây của một account X/Twitter cụ thể | không |
| social_search | Tìm bài đăng X/Twitter theo từ khóa/chủ đề | không |
| lookup | Tìm web/news khi không có URL cụ thể | không |
| fetch | Đọc và trích nội dung từ một URL cụ thể | không |
| format | Định dạng các item đã thu thập thành digest markdown | không |
| send | Gửi nội dung lên Telegram sau khi xác nhận | không, nhưng đã được mở rộng |
| telegram_updates | Đọc updates của bot Telegram và lấy `chat_id` | có |
| policy | Tìm trong policy nội bộ | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải và trích text paper arXiv | không |
| source_quality | Chấm độ tin cậy sơ bộ của một nguồn đã có | có |

## A3. Câu hỏi mẫu để thử

1. `Tin AI hôm nay có gì nổi bật?`
2. `Tóm tắt trang này: https://openai.com/research`
3. `Tìm bài đăng mới nhất của Sam Altman`
4. `Đánh giá độ tin cậy của nguồn này: https://arxiv.org/abs/2401.00001`
5. `Đăng bản tin này lên Telegram giúp tôi`

---

# PHẦN B - Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Measure the original routing quality on the fixed base set. | - | `case_accuracy=0.7143` | `starter_v0/runs/v0_B_base_openai_20260602T145356218324.json` |
| v1 | `system_prompt.md` | A clearer routing policy should reduce missing-info and boundary mistakes. | `case_accuracy=0.7143` | `case_accuracy=0.7` | `starter_v0/runs/v1_B_base_openai_20260602T145746351678.json` |
| v2 | `tools.yaml` | Stronger tool descriptions and custom tool coverage should improve routing clarity. | `case_accuracy=0.7` | `case_accuracy=0.6842` | `starter_v0/runs/v2_B_base_openai_20260602T150141815669.json` |
| v3 | `system_prompt.md` + `tools.yaml` | Final tightening of literal query routing and Telegram boundary handling should stabilize the final behavior. | `case_accuracy=0.6842` | `case_accuracy=0.95` | `starter_v0/runs/v3_B_base_openai_20260602T152606403030.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R12_confirm_before_send | `wrong_boundary` | `clarify` was not selected with `response_type=yes_no` | The agent answered too directly instead of forcing a yes/no confirmation for Telegram posting. | Strengthened the Telegram confirmation guidance in `system_prompt.md`. |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G_SINGLE_001_web_news_today | News/web routing for a current AI topic | `lookup` with `topic=news` and `timeframe=day` | Passed |
| G_SINGLE_002_fetch_url | URL-specific page reading | `fetch` | Passed |
| G_SINGLE_003_no_tool_concept | Stable conceptual question should not call a tool | Direct answer, no tool | Passed |
| G_SINGLE_004_confirm_send | Telegram send boundary requires confirmation | `clarify` with `response_type=yes_no` | Passed |
| G_SINGLE_005_source_quality | Evaluate an already known source | `source_quality` | Passed |
| G_MULTI_001_missing_then_lookup | Multi-turn carryover after missing entity is supplied | `lookup` with carried news intent | Passed |
| G_MULTI_002_missing_then_fetch | Multi-turn URL supply after clarification | `fetch` | Passed |
| G_MULTI_003_search_type_carryover | Preserve topic, limit, and search type across turns | `social_search` | Passed |
| G_MULTI_004_switch_social_to_web | Switch from social to web-news routing | `lookup` | Passed |
| G_MULTI_005_send_confirmation | Telegram post confirmation in multi-turn context | `clarify` with `response_type=yes_no` | Passed |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Tin AI hôm nay có gì nổi bật?` | `lookup` | `starter_v0/transcripts/v3_openai_streamlit_20260602T164336736775.transcript.json` | Assistant returned a research summary grounded in web results. |
| 2 | `Tóm tắt bài viết này giúp mình` | `clarify` | `starter_v0/transcripts/v3_openai_streamlit_20260602T164336736775.transcript.json` | Assistant correctly asked for the missing URL. |
| 3 | `Đăng lên Telegram giúp tôi` | `clarify` | `starter_v0/transcripts/v3_openai_streamlit_20260602T164336736775.transcript.json` | Assistant followed the confirmation-first Telegram policy. |
| 4 | `giá vàng Việt Nam hôm nay` | `lookup` | `starter_v0/transcripts/v3_openai_streamlit_20260602T164336736775.transcript.json` | Assistant kept researching and asked for more specificity when search results were weak. |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `starter_v0/tools/send/tool.py`, `starter_v0/transcripts/v3_openai_streamlit_20260602T164336736775.transcript.json` | Messages send only after explicit confirmation, and `chat_id` can be overridden when needed. | Confirmation is required; the tool is side-effecting by design. |
| arXiv/company policy | `starter_v0/tools/policy/`, `starter_v0/tools/papers/`, `starter_v0/tools/paper_text/` | The agent can research policy and papers using the existing tool set. | Must keep outputs source-grounded. |
| UI | `starter_v0/streamlit_app.py` | Streamlit chat works as a usable front end with visible tool traces and a Telegram status panel. | UI mirrors the same agent/tool loop, so behavior stays consistent with CLI and eval. |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`? Telegram confirmation policy, literal query routing, and when to use `clarify` versus direct answer.
- Which fixes belonged in `tools.yaml`? Tool descriptions, input expectations, and the split between search/fetch/action behavior.
- Which failure needed manual review instead of automatic grading? The Telegram posting boundary, because it depends on conservative interpretation of user intent.
- What would you improve next? Add a dedicated Streamlit send workflow with explicit preview/confirm/send steps so the Telegram path is even easier to demo.

## Team Notes

- Trần Quốc Khánh - 2A202600679: drove the routing and evaluation alignment, including prompt/tool refinement and the final evidence pass.
- Nguyễn Văn Huy - 2A202600773: supported the Telegram and Streamlit delivery path, including the operational checks that make the UI useful in practice.
- Nguyễn Anh Kiệt - 2A202600677: contributed to the research-tool expansion and the report/evidence structure that makes the final submission easy to review.
