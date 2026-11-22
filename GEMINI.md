# SlideWright - Studio trên Gemini CLI

Extension này có hai skill: `make-slides` (tạo, nâng cấp slide, chuyển PDF thành PowerPoint) và `presentation-script` (kịch bản thuyết trình). Hai skill được viết cho Claude; khi chạy trên Gemini CLI, áp dụng các quy ước dưới đây. Phần còn lại của SKILL.md làm đúng như viết.

## Đường dẫn
- Thư mục extension là thư mục chứa tệp GEMINI.md này (thường là `~/.gemini/extensions/slidewright-studio/`). Ở đây gọi là `<EXT>`.
- Chỗ nào SKILL.md hoặc `references/` ghi `${CLAUDE_PLUGIN_ROOT}` thì hiểu là `<EXT>`. Không chạy `find /` để tìm script.
- Tệp kết quả (.pptx, .ppsx, .docx, ảnh kiểm tra) ghi vào thư mục làm việc hiện tại của người dùng, không ghi vào `<EXT>`.

## Chuẩn bị lần đầu
Trước lần dựng đầu tiên, kiểm tra `<EXT>/node_modules`. Nếu chưa có, nói cho người dùng biết sẽ cài gì rồi chạy:
```
npm install --prefix <EXT>
pip install -r <EXT>/requirements.txt
```
Chạy mọi script Node (kể cả script dựng viết trong thư mục làm việc) với `NODE_PATH=<EXT>/node_modules`. Bỏ qua các lệnh `npm install`/`pip install` rải trong `references/` nếu hai lệnh trên đã chạy.

Bước render ảnh cần LibreOffice (`soffice`) và `pdftoppm` (gói poppler). Thiếu thì vẫn dựng và chạy các script kiểm tra, bỏ bước render và nói rõ với người dùng là chưa xem được ảnh từng slide.

## Thay cho công cụ của Claude
| Trong SKILL.md | Trên Gemini CLI |
|---|---|
| AskUserQuestion | Hỏi trong hội thoại, gộp tối đa 4 câu, mỗi câu có các phương án đánh số, phương án đề xuất đặt đầu và ghi "(Đề xuất)". Ảnh xem trước phong cách: lưu PNG và báo đường dẫn. |
| Danh sách công việc (task list) | Công cụ danh sách việc của Gemini CLI nếu có; không có thì liệt kê các bước một lần ở đầu. |
| WebSearch / WebFetch | Công cụ tìm kiếm Google và đọc trang web của Gemini CLI. |
| SendUserFile | Báo đường dẫn tệp đã ghi trong thư mục làm việc. |
| Xem ảnh render | Đọc tệp PNG bằng công cụ đọc tệp. |
| Skill `pptx` (đọc SKILL.md của nó) | Không có. Bỏ qua; quy tắc pptxgenjs đã đủ trong `references/quy-trinh-pptx.md`. |
| `validate.py` của skill pptx | `python3 <EXT>/skills/make-slides/scripts/kiem_tra_goi.py <tệp>.pptx` → phải PASSED. |
| Script `soffice` của skill pptx | `soffice --headless --convert-to pdf --outdir <thư mục> <tệp>.pptx` (gọi `MS.installFontsForPreview` trước). |
| `markitdown` (đọc .pptx cần nâng cấp) | Đọc văn bản bằng python-pptx. |

## Phạm vi của bản Gemini
- Chỉ xuất **PowerPoint** (.pptx + .ppsx, thêm PDF khi bối cảnh yêu cầu). Người dùng xin Canva hoặc Gamma thì nói một câu là bản Gemini chưa hỗ trợ và làm bản PowerPoint.
- Không có Unsplash: cần ảnh thì dùng ảnh người dùng gửi, hoặc vẽ minh hoạ SVG theo mục *Ảnh* của SKILL.md.
