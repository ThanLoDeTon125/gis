# Hướng dẫn chụp lại sách để OCR

Viết cho dự án RAG dược liệu (Sankit). Mọi khuyến nghị dưới đây rút ra từ việc
**đo trực tiếp trên chính ảnh bạn đã chụp**, không phải lý thuyết chung.

---

## Vì sao phải chụp lại

| Sách | Tình trạng ảnh hiện tại | Kết quả OCR |
|---|---|---|
| GACP | Tương đối phẳng, chụp thẳng | Tesseract **90,6%** — dùng được |
| 100 vị thuốc | Trang cong theo gáy, có ngón tay, lọt trang bên cạnh | Tesseract **hỏng** vùng cong |

Khác biệt **không nằm ở máy ảnh** mà ở cách chụp. Chụp đúng thì Tesseract miễn phí
là đủ, **không cần trả tiền cho API nào cả**.

Ngoài ra sách GACP **thiếu hẳn ~50 trang chưa từng được chụp** (xem danh sách ở
mục 6) — phần này OCR không cứu được, bắt buộc phải chụp bổ sung.

---

## 1. Cách nhanh nhất: dùng app quét tài liệu (KHUYÊN DÙNG)

Đừng dùng app Camera thường. Hãy dùng app quét tài liệu — chúng **tự làm phẳng
trang cong, tự cắt đúng mép, tự tăng tương phản**, tức là tự xử lý đúng 3 lỗi đã
làm hỏng bộ ảnh cũ.

Trên iPhone, chọn một trong các cách:

- **Ghi chú (Notes)** → tạo ghi chú mới → biểu tượng máy ảnh → *Quét tài liệu*.
  Đặt chế độ **Tự động**, đưa máy lên là nó tự chụp và tự nắn phẳng.
- **Google Drive** → nút `+` → *Quét* (Scan).
- **Microsoft Lens** (miễn phí) → chế độ *Document*.

App quét cho kết quả tốt hơn hẳn chụp tay, và nhanh hơn vì chụp liên tục được.

---

## 2. Bốn nguyên tắc quan trọng nhất

Xếp theo mức ảnh hưởng tới chất lượng OCR:

**a) Trang phải PHẲNG — quan trọng nhất**

Đây là thứ đã phá hỏng sách 100 vị thuốc. Chữ gần gáy bị cong vào trong, OCR đọc
thành ký tự vô nghĩa.

- Mở sách và **ép sát xuống mặt bàn**, dùng tay đè ở *lề ngoài*, không đè lên chữ.
- Tốt nhất: đặt một **tấm kính hoặc mica trong** lên trang để ép phẳng hoàn toàn.
- Nếu sách dày khó mở phẳng, kê một cuốn sách khác đỡ dưới bìa cho cân.

**b) MỘT trang cho một ảnh**

Ảnh cũ lọt cả cột chữ của trang bên cạnh, khiến OCR trộn lẫn hai trang vào nhau.

- Chỉ đưa **đúng một trang** vào khung hình.
- Cho trang **chiếm gần hết khung**, chừa lề khoảng 1cm.
- Che trang đối diện bằng một tờ giấy trắng nếu cần.

**c) Máy ảnh THẲNG GÓC với trang**

- Ống kính nằm **ngay chính giữa trang, chiếu thẳng xuống**, không nghiêng, không chếch.
- Bốn cạnh trang trong ảnh phải **song song với bốn cạnh khung hình**.
- Bật lưới (Cài đặt → Camera → Lưới) để canh cho dễ.

**d) KHÔNG để ngón tay che chữ**

- Đè ở **mép ngoài cùng**, ngoài vùng có chữ.
- Hoặc dùng vật chặn: thước, kẹp giấy, chai nước nhỏ.

---

## 3. Ánh sáng

- **Ánh sáng đều, khuếch tán**. Gần cửa sổ ban ngày là tốt nhất.
- **Tắt flash** — flash gây loá trên giấy bóng và làm mất chữ.
- Coi chừng **bóng của chính bạn / của điện thoại** đổ lên trang. Đứng lệch sang
  bên, hoặc dùng hai nguồn sáng hai bên.
- Không chụp dưới một bóng đèn duy nhất ngay trên đầu (dễ tạo vệt sáng giữa trang).

---

## 4. Thiết lập máy ảnh

- **Chạm vào giữa trang để lấy nét** trước mỗi lần chụp, chờ nét rồi mới bấm.
- Giữ máy chắc, hoặc kê lên chồng sách / dùng chân kẹp cho khỏi rung.
- Độ phân giải: ảnh cũ của bạn khoảng 2600×3500 px — **mức này đã đủ tốt**, không
  cần cao hơn. Đừng bật chế độ 48MP, chỉ làm file nặng thêm.
- Định dạng: JPG hoặc PDF đều được.

---

## 5. Đừng bỏ sót trang

Sách GACP hiện thiếu ~50 trang vì bỏ sót lúc chụp. Cách tránh:

- Chụp **tuần tự**, không nhảy cóc.
- Cứ khoảng 20 trang thì **dừng lại đối chiếu số trang in trên sách** với số ảnh
  đã chụp — hai con số phải khớp.
- Chụp cả **trang chỉ có ảnh minh hoạ** (đừng bỏ qua), để mạch trang không đứt.

---

## 6. Danh sách trang GACP cần chụp bổ sung

Thiếu 57 trang, gom theo từng cây (số là **số trang in trên sách**):

| Cây dược liệu | Khoảng trang cần chụp |
|---|---|
| Mã đề | 258–270, 270–272, 272–289 |
| Actisô | 11–15, 15–19 |
| Độc hoạt | 181–188 |
| Giảo cổ lam | 201–214, 219–222, 223–228 |
| Bạch chỉ | 41–44, 46–49 |
| Cà gai leo | 94–106 |
| Chè vằng | 107–116 |
| Ngưu tất | 293–295, 295–300 |
| Ba kích | 21–26, 29–32 |
| Cúc hoa vàng | 123–136 |
| Đảng sâm Việt Nam | 148–158, 162–168 |
| Đinh lăng | 170–174, 174–181 |
| Đương quy Nhật Bản | 193–199 |
| Sa nhân tím | 339–352 |
| Xuyên khung | 359–367 |
| Xuyên tâm liên | 368–371, 373–379 |
| Bạch truật | 49–61 |
| Bụp giấm | 85–89 |
| Huyền sâm | 236–239 |
| Ích mẫu | 246–252 |
| Nhân trần | 305–307 |
| Rau đắng biển | 311–326 |
| (phần mở đầu) | 9–11 |

---

## 7. Chụp xong thì làm gì

1. Đặt file vào thư mục tương ứng:
   - Sách 100 vị thuốc → `Sankit/books/100_vi_thuoc/`
   - Sách GACP → `Sankit/books/gacp/`
2. **Đặt tên theo thứ tự trang**, ví dụ `trang_001.jpg`, `trang_002.jpg`… hoặc gộp
   thành một PDF duy nhất theo đúng thứ tự. Thứ tự file quyết định thứ tự nội dung
   trong kho tri thức.
3. Giữ lại file cũ, đừng xoá — để còn đối chiếu.
4. Báo lại, hệ thống sẽ chạy OCR bằng Tesseract (miễn phí) và đo chất lượng.

---

## 8. Kiểm tra nhanh trước khi chụp cả cuốn

**Chụp thử 5 trang rồi gửi sang chạy OCR đo điểm trước.** Nếu đạt trên 90% thì cứ
thế chụp tiếp cả cuốn; nếu chưa đạt thì chỉnh cách chụp rồi thử lại. Làm vậy tránh
được cảnh chụp xong 543 trang mới phát hiện sai cách.
