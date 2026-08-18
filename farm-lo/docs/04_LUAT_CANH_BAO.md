# 04 — Luật cảnh báo

Sáu luật, chạy trên **quan trắc thật**. Cài đặt tham chiếu ở `scripts/sinh_du_lieu.py`
mục 11. Khi chuyển sang monorepo thì đây là nội dung của `@sankit/rule-engine`.

Kết quả trên bộ dữ liệu: **89 cảnh báo** — 22 `cao`, 55 `trung_binh`, 12 `thap`;
84 theo lô, 5 theo farm.

---

## R1 · THIEU_NUOC — 56 cảnh báo

**Bắt:** ETc vượt mưa hiệu quả trong một cửa sổ trượt.

```
cửa sổ    = 15 ngày, trượt từng ngày trên khí hậu NGÀY
ETc       = Σ ( Kc(lô, tháng) × ET0(ngày) )
mưa_hq    = Σ ( P(ngày) nếu P ≥ 5 mm, ngược lại 0 )
báo khi   thiếu = ETc − mưa_hq ≥ 25 mm
mức       cao nếu thiếu ≥ 45 mm, ngược lại trung_binh
```

Các cửa sổ liên tiếp cùng vượt ngưỡng được **gộp thành một đợt**, giữ giá trị đỉnh.
Lô `cong_trinh` bị loại khỏi luật.

**Vì sao tính theo ngày chứ không theo tháng.** Đợt hạn thật của kỳ này kéo 18 ngày từ
30/03/2026 — vắt qua hai tháng. Gộp theo tháng thì nó bị chia đôi: tháng 3 hụt 47 mm,
tháng 4 hụt 75 mm cho lô đang gieo, nhưng với hai vườn chanh (Kc 0,70) thì cả hai tháng
đều **dưới ngưỡng**, không báo gì. Trong khi đó ảnh vệ tinh cho thấy chính hai lô chanh
sụt nặng nhất farm: L04 −0,318, L07 −0,286.

Cửa sổ trượt 15 ngày cho L07 cảnh báo mức `cao`: *hụt 51 mm (30/03 → 17/04)*.

**Vì sao bỏ mưa dưới 5 mm/ngày.** Mưa nhỏ trên đất trống bốc hơi gần hết trong ngày,
không xuống tới tầng rễ. Cộng vào là thổi phồng lượng nước cây thật sự nhận được.

**Chưa làm:** chưa có mô hình cân bằng nước trong đất (soil water balance) — mới là
hiệu hai đại lượng, chưa tính sức chứa ẩm hữu hiệu của tầng rễ. SoilGrids đã có đủ số
liệu (`bdod`, `clay`, `sand`) để làm bước này.

---

## R2 · SUT_NDVI_KHONG_RO_LY_DO — 5 cảnh báo

**Bắt:** tán giảm mạnh mà không ai ghi việc gì.

```
báo khi   NDVI(t₁) − NDVI(t₀) ≤ −0,20
          và t₁ − t₀ ≤ 45 ngày
          và không có bản ghi `thu_hoach` hay `cai_tao_dat` nào trong [t₀−10, t₁+10]
mức       cao nếu sụt ≤ −0,35 VÀ không trùng đợt hạn, ngược lại trung_binh
```

Ngày nằm trong `NGAY_DANG_NGO` (mù khí quyển hoặc quá ít lô có pixel quang) bị loại
trước khi luật chạy — nếu không thì mỗi ngày mù đẻ ra 12 cảnh báo giả.

**Hạ mức khi trùng đợt hạn.** Sụt NDVI trong cửa sổ hạn nhiều khả năng là stress nước
chứ không phải việc của người. Cảnh báo vẫn ra, nhưng ở mức `trung_binh` và mang cờ
`trung_dot_han: true` để giao diện nhóm chung với R1.

**5 cảnh báo đang có, và đọc chúng thế nào:**

| Lô | Ngày | Sụt | Đọc là gì |
|---|---|---:|---|
| L08 | 21/09/2025 | −0,371 | chưa rõ — không có bản ghi nào |
| L09 | 21/09/2025 | −0,410 | lô nghỉ, thảm tự nhiên tàn theo mùa |
| L10 | 04/10/2025 | −0,258 | vườn ươm xuất cây giống, chưa được ghi |
| L04 | 07/04/2026 | −0,318 | **trùng đợt hạn** |
| L07 | 07/04/2026 | −0,286 | **trùng đợt hạn** |

---

## R3 · MAT_DAU_QUANG_HOC — 5 cảnh báo

**Bắt:** khoảng trống ảnh quang đủ dài để mất dấu một sự kiện đồng ruộng.

```
báo khi   khoảng cách hai lần quan trắc quang liên tiếp ≥ 30 ngày
phạm vi   nếu ≥ 8/12 lô cùng thủng một khoảng → MỘT cảnh báo mức farm
          ngược lại → cảnh báo riêng từng lô
mức       thap nếu có ≥ 4 ngày radar bù trong khoảng, ngược lại trung_binh
```

**Vì sao phải gộp về mức farm.** Mây phủ cả vùng chứ không chọn lô. Không gộp thì bốn lỗ
hổng của kỳ này đẻ ra 48 cảnh báo, tất cả nói cùng một chuyện. Sau khi gộp còn 5.

Năm khoảng thủng của kỳ này — bốn cái phủ cả farm, một cái riêng L10:

| Khoảng | Dài | Phạm vi |
|---|---:|---|
| 20/08 → 21/09/2025 | 32 ngày | 11/12 lô |
| 20/08 → 04/10/2025 | 45 ngày | riêng L10 |
| 04/10 → 13/11/2025 | 40 ngày | cả 12 lô |
| **18/12/2025 → 13/03/2026** | **85 ngày** | cả 12 lô |
| 12/04 → 27/05/2026 | 45 ngày | cả 12 lô |

Khoảng 85 ngày trùng đúng giai đoạn làm đất và gieo lạc xuân (05/02/2026) — nghĩa là
**không có ảnh quang nào chứng kiến vụ đó bắt đầu**. Trong khoảng ấy Sentinel-1 vẫn bay
đều, và đó là lý do radar nằm trong pipeline chứ không phải để cho đủ món.

---

## R4 · KEM_MAT_BANG_FARM — 11 cảnh báo

**Bắt:** lô liên tục kém hơn mặt bằng chung, không phải kém một lúc.

```
báo khi   NDVI(lô, ngày) − trung_vị_12_lô(ngày) ≤ −0,15
          xảy ra 3 lần quan trắc LIÊN TIẾP
```

Dùng **trung vị theo ngày** chứ không dùng trung bình cả kỳ: so cùng ngày thì tự động
loại được ảnh hưởng của thời tiết, mùa vụ và chất lượng ảnh — cả 12 lô cùng chịu.

Đếm liên tiếp reset về 0 khi có một lần quan trắc không vượt ngưỡng. Sau khi bắn thì
reset để không bắn lặp trên cùng một chuỗi dài.

---

## R5 · NHAT_KY_KHONG_KHOP_ANH — 11 cảnh báo

**Đây là luật mang giá trị thương mại của cả mô hình.** Nó đối chiếu **lời khai** với
**số đo độc lập**.

```
với mỗi đợt thu hoạch khai báo [t₁, t₂] của một vụ:
  đỉnh_trước = NDVI lớn nhất trong [t₁ − 45 ngày, t₁]
  đáy_sau    = NDVI nhỏ nhất  trong [t₂, t₂ + 45 ngày]
  sụt        = đáy_sau − đỉnh_trước
  khớp khi   sụt ≤ ngưỡng(cây)
```

**Lấy đỉnh–đáy chứ không lấy hai điểm kề mốc.** Cúc chi hái nhiều đợt suốt 5 tuần, tán
đã bắt đầu xuống từ trước ngày ghi "bắt đầu thu". Đo bằng hai điểm kề mốc thì L01 chỉ
ra −0,097 và bị chấm là "không thấy"; đo đỉnh–đáy ra **−0,424**, đúng thực tế.

### Ngưỡng khác nhau theo cây

| Cây | Ngưỡng | Vì sao |
|---|---:|---|
| Lạc | −0,25 | nhổ cả cây, tán biến mất |
| Cúc chi | −0,20 | hái hoa nhiều đợt rồi phá luống cuối vụ |
| Cúc cổ, bồ công anh | −0,08 | cắt phần trên, gốc giữ nguyên, tái sinh nhanh |
| Luống ươm | −0,05 | xuất cây giống, nền luống vẫn còn |
| **Chanh** | **không áp dụng** | hái quả không đụng tới tán — vệ tinh không kiểm được |

Không có dòng cuối thì mọi đợt hái chanh (10 lô hàng trong bộ này) đều thành báo động giả.
Với chanh, bằng chứng phải là cân tại vườn và ảnh chụp có GPS.

### Radar là lớp thứ hai

Khi ảnh quang không kết luận được, so VH radar trung bình 30 ngày trước `t₁` với 30 ngày
sau `t₂` (trung bình trên **thang tuyến tính** rồi mới đổi sang dB — dB là hàm log, lấy
trung bình thẳng trên dB là sai). Ngưỡng −0,5 dB.

| Kết quả tổng hợp | Số đợt | Nghĩa |
|---|---:|---|
| `xac_nhan` | 7 | quang thấy |
| `xac_nhan_bang_radar` | 3 | quang không thấy, radar thấy → **cây chỉ chiếm một phần lô** |
| `can_nguoi_xac_minh` | 3 | cả hai đều không thấy → có chuyện |
| `chua_ket_luan_duoc` | 5 | thiếu ảnh một phía |
| `khong_ap_dung` | 4 | chanh |

Ba ca `can_nguoi_xac_minh`: **L06** (khai thu hoạch trên khu công trình — bản ghi sai
cắm cố ý), **L10** (vườn ươm trồng hỗn hợp), **L05** (sụt −0,078 so với ngưỡng −0,08,
sát ngưỡng).

---

## R6 · CHUOI_NGAY_KHONG_MUA — 1 cảnh báo

```
báo khi   ≥ 14 ngày liên tiếp mưa dưới 1 mm
phạm vi   farm
mức       cao nếu ≥ 18 ngày
```

Kỳ này có đúng một đợt: **18 ngày, 30/03 → 17/04/2026**. Nó là nền của mọi cảnh báo R1
cùng kỳ và là cách giải thích cho hai cảnh báo R2 ngày 07/04. Giao diện nên gộp chúng
thành một sự kiện thay vì liệt kê rời.

---

## Chỗ cần chỉnh khi lên sản xuất

1. **Ngưỡng phải cấu hình được theo vườn, không hard-code.** Farm khác, cây khác, khí
   hậu khác.
2. **Cảnh báo phải có vòng đời**: `mo` → `da_xem` → `da_xu_ly` / `bo_qua` kèm lý do.
   Bộ dữ liệu này mới sinh ra cảnh báo, chưa có trạng thái xử lý.
3. **Chống bắn lặp.** Mỗi lần có ảnh mới mà chạy lại toàn bộ là cảnh báo cũ ra lại.
   Cần khoá theo `(ma_luat, lo_id, cửa_sổ_thời_gian)`.
4. **R1 nên nâng thành cân bằng nước trong đất**, dùng `bdod`/`clay`/`sand` của SoilGrids
   để tính sức chứa ẩm hữu hiệu.
5. **Chưa có luật cho radar đứng riêng.** Radar có 57/57 ngày dùng được, dày gấp 2,6 lần
   ảnh quang; hiện chỉ dùng để bù cho R5. Một luật dựa trên VH sẽ chạy được cả trong mùa mây.
