# Xác định phong cách từ đề tài

Đề tài **do người dùng cung cấp**. Claude dùng tài liệu này để **gợi ý 3 phong cách** phù hợp nhất (1 đề xuất + 2 phương án), kèm lý do và ảnh xem trước; **người dùng chọn**. Thông số máy đọc được (phông, màu) nằm ở `assets/styles.json` — dùng trực tiếp khi dựng slide.

## 1. Mười một phong cách

Phân theo ba mức trang trọng. Mức quyết định **phông** (xem `phong-chu.md`): *chính quy* chỉ dùng phông có chân (serif) / không chân (sans-serif); *bán chính quy* được dùng phông trưng bày và phông viết tay dễ đọc cho điểm nhấn; *kiểu cách* được dùng phông trang trí cho tiêu đề nghệ thuật, WordArt.

### Mức CHÍNH QUY

**1. Sang trọng – Thanh lịch** (`sang-trong`)
- Đề tài: báo cáo tổng kết/sơ kết, báo cáo hội nghị, báo cáo trước lãnh đạo, giới thiệu đơn vị, đề án, lễ trao giải trang trọng, kết quả thi đua.
- Cảm giác: chững chạc, cao cấp, tự tin.
- Phông: Noto Serif Display (tiêu đề) + Montserrat (nội dung, con số).
- Màu: xanh đêm 14213D làm chủ đạo, vàng kim C9A227 cho hình khối, chữ nhấn trên nền đậm màu sâm panh nhạt (vàng kim tươi trên xanh đêm là cặp gần đối nhau), nhiều trắng.
- Bố cục: nhiều khoảng trắng; số liệu lớn (60–96pt) đứng một mình; ảnh tràn viền có lớp phủ tối; biểu đồ tối giản. Motif: đường viền mảnh vàng kim quanh khung ảnh hoặc số thứ tự lớn mờ.
- Hiệu ứng: fade, floatUp, zoom cho số liệu; chuyển trang fadeBlack giữa các phần, fade/push trong phần; Morph cho số liệu.

**2. Nghiêm túc – Học thuật** (`hoc-thuat`)
- Đề tài: triết học, lý luận chính trị, tư tưởng, đạo đức học, nghiên cứu khoa học, chuyên đề lý luận văn học, bảo vệ luận văn/đề tài, sinh hoạt chuyên môn chuyên sâu.
- Cảm giác: sâu sắc, chặt chẽ, tĩnh — **nhấn mạnh bằng phông có chân**.
- Phông: Lora (tiêu đề, đậm) + Noto Serif (nội dung); trích dẫn dùng Lora nghiêng cỡ lớn. Toàn bài là serif.
- Màu: đen than 1F1F1F, nền trắng, đỏ rượu 7B1E2B làm nhấn (trên nền tối dùng đồng nhạt D9B38C).
- Bố cục: trích dẫn lớn có nguồn; sơ đồ khái niệm (khối – mũi tên); hai cột luận điểm – luận cứ; ít ảnh, ảnh đen trắng hoặc chân dung tác giả có nguồn.
- Hiệu ứng: tiết chế trong mức phong phú — fade, wipe từng dòng (byPara) cho luận điểm, split cho trích dẫn; chuyển trang fade; Morph cho sơ đồ phát triển dần.

**3. Trang trọng – Hành chính** (`hanh-chinh`)
- Đề tài: triển khai nhiệm vụ năm học, kế hoạch, hướng dẫn, quy chế, công văn, tập huấn chuyên môn, phổ biến văn bản.
- Cảm giác: chuẩn mực, rõ ràng, đáng tin.
- Phông: Noto Serif (tiêu đề) + Montserrat (nội dung).
- Màu: xanh lam đậm 0B3C7D, đỏ C8102E làm nhấn nhỏ (trên nền tối dùng vàng FFD54F), nền trắng.
- Bố cục: đánh số mục rõ (I, II, 1, 2); bảng nhiệm vụ – thời gian – đơn vị; dòng thời gian; hộp "căn cứ văn bản". Trích dẫn văn bản ghi đúng số, ký hiệu, ngày ban hành.
- Hiệu ứng: wipe từng dòng, fade, fly cho bước quy trình; chuyển trang push trong phần, fade giữa các phần.

**4. Truyền thống – Văn hoá** (`truyen-thong`)
- Đề tài: lịch sử, di sản, văn hoá dân tộc, giáo dục địa phương, lễ hội, nghề truyền thống, danh nhân, địa danh.
- Cảm giác: trầm ấm, gần gũi, tự hào.
- Phông: Noto Serif Display (tiêu đề) + Lora (nội dung).
- Màu: nâu phù sa 5B2C1A, đỏ son B23A28, vàng đất A9782F (phối tương đồng ấm, không đặt đỏ son cạnh xanh lúa); trên nền tối nhấn màu ngà F5E6C8.
- Bố cục: ảnh tư liệu lớn kèm chú thích nguồn; dòng thời gian lịch sử; bản đồ; hoạ tiết dân gian rất nhẹ ở góc slide chia phần.
- Hiệu ứng: fade, wipe cho dòng thời gian, Morph phóng ảnh nhỏ thành ảnh tràn viền; chuyển trang fade/wipe.

**5. Rõ ràng – Sư phạm** (`su-pham`)
- Đề tài: bài giảng THCS–THPT, chuyên đề dạy học, ôn tập, hướng dẫn học sinh.
- Cảm giác: mạch lạc, dễ theo dõi, tập trung.
- Phông: tiêu đề Playfair Display (Ngữ văn, Lịch sử, GDCD, KHXH) hoặc Bricolage Grotesque (Toán, KHTN, Tin, Công nghệ) + Lexend (nội dung, dễ đọc).
- Màu: xanh ngọc đậm 064E57, nền trắng/ngọc nhạt E6F4F1, vàng mù tạt F2C14E làm nhấn (chữ nhấn trên nền sáng 896701). Không dùng san hô/cam cạnh xanh ngọc (màu đối nhau).
- Bố cục: theo tiến trình bài học (khởi động → mục tiêu → kiến thức → luyện tập → vận dụng → tổng kết); câu hỏi và đáp án ở slide/cú nhấp riêng; sơ đồ tư duy tổng kết.
- Hiệu ứng: byPara cho ý kiến thức, appear/zoom cho đáp án, fly cho thẻ; chuyển trang push trong phần, split cho slide chia hoạt động.

**6. Hiện đại – Tối giản** (`hien-dai`)
- Đề tài: đổi mới, chiến lược, kế hoạch phát triển, dự án, sáng kiến, khởi nghiệp, kỹ năng.
- Cảm giác: gọn, mạnh, hướng tới tương lai.
- Phông: Bricolage Grotesque (tiêu đề) + Montserrat (nội dung).
- Màu: than chì 22252B, nền trắng, cam FF6B35 làm nhấn duy nhất.
- Bố cục: chữ lớn ít chữ; lưới thẻ; một ý một slide; ảnh cắt hình học.
- Hiệu ứng: Morph nhiều, zoom, push; chuyển trang Morph/push.

**7. Công nghệ – Số** (`cong-nghe`)
- Đề tài: chuyển đổi số, AI, STEM, tin học, dữ liệu, phần mềm, an toàn thông tin.
- Cảm giác: hiện đại, chính xác, năng động.
- Phông: Bricolage Grotesque (tiêu đề) + Lexend (nội dung) + Space Mono (số liệu, nhãn kỹ thuật).
- Màu: xanh đen 0A1931 (bìa, chia phần, slide tuyên bố), cyan 00D1FF cho hình khối và biểu đồ, chữ nhấn trên nền tối xanh bạc hà 7CFFB2 (tương đồng, không dùng cam/hổ phách đối với xanh, không dùng chữ xanh nhạt cùng tông nền), nền nội dung trắng/xanh rất nhạt EAF1F8.
- Bố cục: nhịp tối – sáng (nền tối cho slide mở phần, nền sáng cho slide nội dung); sơ đồ hệ thống; số liệu dạng bảng điều khiển; ảnh chụp màn hình trong khung thiết bị.
- Hiệu ứng: Morph, wipe, zoom, cover; chuyển trang Morph/cover.

### Mức BÁN CHÍNH QUY

**8. Sinh động – Trẻ trung** (`sinh-dong`)
- Đề tài: phong trào, ngoại khoá, Đoàn – Đội, câu lạc bộ, hội thi học sinh, ngày hội đọc sách, trải nghiệm.
- Phông: Rowdies (tiêu đề) + Montserrat Alternates (nội dung) + Dancing Script (điểm nhấn ngắn).
- Màu: xanh tím than 2F3C7E, san hô F96167, tím oải hương B8A1FF; trên nền tối nhấn hồng nhạt FFB3C1 (không vàng/cam trên nền tím than).
- Bố cục: ảnh hoạt động dạng lưới; con số ấn tượng; hình khối bo tròn, nghiêng nhẹ.
- Hiệu ứng: dùng đủ danh mục (fly, zoom, pulse, wheel); chuyển trang đa dạng theo phần.

**9. Thân thiện – Thiếu nhi** (`thieu-nhi`)
- Đề tài: bài giảng tiểu học, mầm non, sinh hoạt lớp, họp phụ huynh tiểu học, trò chơi học tập.
- Phông: Baloo 2 (tiêu đề) + Nunito (nội dung) + Pangolin (câu hỏi, lời nhắn vui).
- Màu: xanh lam 2D3A8C với hồng san hô FF6F91, xanh trời 4FC3F7, tím oải hương B39DFF; nền trắng/lam nhạt EEF2FF (không ghép cam–lam, đỏ–lục).
- Bố cục: chữ to (nội dung ≥ 24pt), ít chữ, nhiều hình minh hoạ, biểu tượng lớn; mỗi slide một nhiệm vụ.
- Hiệu ứng: đủ danh mục, nhấn mạnh pulse khi khen/đáp án; chuyển trang Morph với cảnh `manhHinh` (mảnh hình bay xoay), lướt `pan`, `push`.

### Mức KIỂU CÁCH

**10. Lễ kỷ niệm – Tri ân** (`le-ky-niem`)
- Đề tài: 20/11, khai giảng, bế giảng, kỷ niệm thành lập, tri ân, chào mừng, lễ tuyên dương.
- Phông: Playfair Display (tiêu đề) + Montserrat (nội dung) + Great Vibes / Style Script (chữ nghệ thuật: "Tri ân", "Chào mừng", "Trân trọng cảm ơn").
- Màu: đỏ đô 8B0000, vàng kim D4A017 (trên nền tối F2C14E).
- Bố cục: bìa và kết thúc nền đậm có chữ nghệ thuật lớn; ảnh kỷ niệm; trích lời tri ân.
- Hiệu ứng: zoom, floatUp, Morph; chuyển trang Morph với cảnh `chuNen`, `quyDao`; `fadeBlack`, `reveal` cho mở đầu và slide cảm ơn.

**11. Kiểu cách – Nghệ thuật** (`nghe-thuat`)
- Đề tài: văn nghệ, thơ ca, giới thiệu tác phẩm/tác giả theo hướng cảm thụ, triển lãm, thiệp, WordArt, câu lạc bộ văn học.
- Phông: Playfair Display nghiêng (tiêu đề) + Lora (nội dung) + Allura / Beau Rivage / WindSong (chữ nghệ thuật cỡ rất lớn, 1–3 từ).
- Màu: tím than 3B1E54, hồng sen D9467A, hồng phấn E8B4B8.
- Bố cục: ảnh nghệ thuật tràn viền; câu thơ đứng một mình giữa nhiều khoảng trắng; chữ nghệ thuật làm điểm nhìn.
- Hiệu ứng: fade chậm (dur 1000–1500), floatUp, split; chuyển trang fade/Morph.

## 2. Quy tắc màu dùng chung
Mỗi phong cách trong `styles.json` có: `dark` (nền đậm, chữ trên nền sáng), `light`, `soft` (nền thẻ), `muted` (chữ phụ), `accent` (hình khối, biểu tượng, nền thẻ nhấn), `accentText` (chữ nhấn trên nền sáng, đạt tương phản ≥ 4.5:1), `accentOnDark` (chữ nhấn trên nền đậm, ≥ 4.5:1). **Không dùng `accent` làm màu chữ trên nền sáng** — dùng `accentText`. Không phối hai màu đối nhau (lam–cam, đỏ–lục, vàng–tím) theo `phoi-mau.md`. `accentOnDark` phải lệch sắc ≥ 30° so với `dark` hoặc là màu gần trung tính (trắng, ngà) — không dùng chữ xanh nhạt trên nền xanh đậm. `surfaceDark` (nếu có) là màu thẻ trên nền đậm. Khi tự pha màu cho người dùng, gọi `style()` và xem cảnh báo bảng màu trước khi dựng.

## 3. Quy trình suy ra phong cách
1. **Phân tích đề tài** thành ba yếu tố:
   - *Mục đích*: báo cáo · triển khai · giảng dạy · nghiên cứu · kỷ niệm · truyền cảm hứng · giới thiệu.
   - *Lĩnh vực*: triết học/lý luận · văn học · lịch sử/văn hoá · KHTN · công nghệ · quản lý giáo dục · hoạt động học sinh.
   - *Người nghe* (nếu đề tài hoặc tài liệu cho biết): lãnh đạo · giáo viên · học sinh (cấp nào) · phụ huynh · cộng đồng.
2. **Chọn theo mục đích trước**, lĩnh vực sau:

| Mục đích | Phong cách mặc định | Ngoại lệ theo lĩnh vực / người nghe |
|---|---|---|
| Báo cáo, tổng kết, đề án | Sang trọng – Thanh lịch | Công nghệ → Công nghệ – Số; báo cáo phong trào học sinh trước học sinh → Sinh động |
| Triển khai, hướng dẫn, quy chế, tập huấn | Trang trọng – Hành chính | Tập huấn công nghệ → Công nghệ – Số |
| Nghiên cứu, lý luận, chuyên đề sâu | Nghiêm túc – Học thuật | Đề tài lịch sử/di sản → Truyền thống – Văn hoá |
| Giảng dạy | Rõ ràng – Sư phạm | Tiểu học/mầm non → Thân thiện – Thiếu nhi; bài triết học/GDCD lớp 12 → Nghiêm túc – Học thuật; bài thơ cần cảm thụ → được mượn tiêu đề Kiểu cách – Nghệ thuật cho bìa |
| Kỷ niệm, tri ân, chào mừng | Lễ kỷ niệm – Tri ân | Kỷ niệm danh nhân/lịch sử → Truyền thống – Văn hoá |
| Giới thiệu, truyền cảm hứng | Hiện đại – Tối giản | Văn hoá, du lịch địa phương → Truyền thống; tác phẩm nghệ thuật → Kiểu cách – Nghệ thuật |
| Hoạt động học sinh, sự kiện | Sinh động – Trẻ trung | Tiểu học → Thân thiện – Thiếu nhi |

3. **Điều chỉnh theo người nghe**: có lãnh đạo cấp trên → nâng lên mức trang trọng hơn một bậc (ví dụ Sinh động → Hiện đại – Tối giản); người nghe nhỏ tuổi → hạ xuống mức thân thiện hơn.
4. **Phối hợp khi đề tài lai** (ví dụ "Báo cáo kết quả Ngày hội đọc sách"): giữ **một phong cách chính** theo mục đích (Sang trọng); được mượn **tối đa một yếu tố** từ phong cách thứ hai (màu nhấn hoặc kiểu ảnh). **Không bao giờ** mượn phông trang trí vào bài mức chính quy.
5. **Gợi ý 3 phương án**: phương án đề xuất là kết quả của bước 2–4; hai phương án còn lại lấy phong cách gần thứ hai và một phong cách khác hướng (trang trọng hơn hoặc mềm mại hơn) để người dùng có lựa chọn thật sự. Không gợi ý phong cách mức kiểu cách cho đề tài chính quy trừ khi người dùng yêu cầu. Mỗi phương án một câu lý do, ví dụ: "Nghiêm túc – Học thuật (Đề xuất): đề tài triết học cần sự chặt chẽ, toàn bộ phông có chân."
6. **Xem trước**: dựng ảnh bằng `scripts/xem_truoc_phong_cach.py` với đề tài thật để người dùng so sánh trực quan trước khi chọn.

## 4. Ví dụ đề tài → phong cách
| Đề tài | Phong cách | Lý do |
|---|---|---|
| Báo cáo tổng kết năm học 2025–2026 | Sang trọng – Thanh lịch | Báo cáo trước lãnh đạo, nhiều số liệu |
| Phép biện chứng duy vật và vận dụng trong đổi mới giáo dục | Nghiêm túc – Học thuật | Triết học, lý luận — nhấn bằng serif |
| Triển khai Kế hoạch kiểm tra, đánh giá học kỳ I | Trang trọng – Hành chính | Triển khai văn bản, nhiệm vụ, mốc thời gian |
| Đờn ca tài tử Nam Bộ – di sản văn hoá phi vật thể | Truyền thống – Văn hoá | Di sản, văn hoá địa phương |
| Bài 3: Đọc hiểu văn bản nghị luận (Ngữ văn 10) | Rõ ràng – Sư phạm (Playfair + Lexend) | Bài giảng THPT, môn KHXH |
| Ứng dụng AI trong soạn kế hoạch bài dạy | Công nghệ – Số | Công nghệ, tập huấn giáo viên |
| Kế hoạch chiến lược phát triển nhà trường 2026–2030 | Hiện đại – Tối giản | Chiến lược, hướng tương lai |
| Ngày hội Đọc sách học sinh THCS | Sinh động – Trẻ trung | Sự kiện học sinh |
| Tiếng Việt lớp 1: Làm quen chữ cái | Thân thiện – Thiếu nhi | Học sinh tiểu học |
| Kỷ niệm 44 năm Ngày Nhà giáo Việt Nam | Lễ kỷ niệm – Tri ân | Lễ kỷ niệm, cần chữ nghệ thuật |
| Giới thiệu tập thơ "Mùa thu trong thơ Việt" | Kiểu cách – Nghệ thuật | Cảm thụ nghệ thuật, chữ trang trí |
