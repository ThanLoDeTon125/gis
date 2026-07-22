# Chiến lược GIS & Carbon

**Tài liệu liên quan:** Tổng quan Sankit · **Tài liệu nguồn:** Báo cáo GIS & Carbon

Một trụ cột chiến lược mới ngoài pitch deck: sử dụng hệ thống thông tin địa lý (GIS)/bản đồ số và giao dịch tín chỉ carbon như hai lớp giá trị được xây dựng trên cùng một bộ dữ liệu không gian dùng chung.

### Luận điểm cốt lõi
Mô hình “dược liệu dưới tán rừng” là điểm giao thoa lý tưởng của cả hai trụ cột. Một khu rừng bảo tồn đồng thời là: một vùng trồng cần truy xuất nguồn gốc (GIS), một bể chứa carbon cần MRV (cũng là GIS), và một tài sản tạo ra hai dòng doanh thu trên cùng một mảnh đất — dược liệu và carbon — từ cùng một bộ dữ liệu nền.

### Vì sao là lúc này — cửa sổ chính sách hiếm có (giữa năm 2026)

Ba sự kiện hội tụ đúng vào thời điểm Sankit quyết định hướng đầu tư:

1. **29/06/2026** — Sàn giao dịch carbon nội địa của Việt Nam chính thức ra mắt (Nghị định 29/2026/NĐ-CP); hạ tầng giao dịch hiện đã sẵn sàng.
2. **01/07/2026** — Nghị định 180/2026/NĐ-CP có hiệu lực: siết chặt và hợp pháp hóa việc giao dịch tín chỉ carbon rừng qua sàn hoặc hợp đồng thương mại; cấm bán trùng (double-selling); giới hạn xuất khẩu tối đa 50% đối với tín chỉ carbon rừng.
3. **01/07/2026** — Hệ thống truy xuất nguồn gốc nông sản quốc gia đi vào hoạt động sau 6 tháng thí điểm với sầu riêng; Sankit nên thiết kế hệ thống để kết nối qua API thay vì xây dựng một hệ thống đóng.

### GIS — ba mục đích, một lớp nền

Cả ba mục đích đều dùng chung một đa giác (polygon) vùng trồng; cần được xây dựng theo thứ tự sau (lớp sau tận dụng dữ liệu của lớp trước):

1. **Truy xuất nguồn gốc (làm trước).** Mỗi vùng trồng có một mã định danh (Plot ID) duy nhất + đa giác GeoJSON được thu thập qua thiết bị ngay tại thực địa, liên kết với hồ sơ canh tác (giống cây, ngày tháng, quy trình GACP-WHO, ảnh có gắn thẻ tọa độ/thời gian). Mỗi lô hàng sẽ kế thừa Plot ID để truy xuất từ đầu đến cuối. **Động lực:** hệ thống quốc gia (đang hoạt động) + EUDR (Quy định chống phá rừng của EU) — yêu cầu định vị vùng trồng (điểm GPS cho diện tích <4 ha, đa giác cho >4 ha) + bằng chứng vệ tinh không phá rừng sau 31/12/2020, hạn chót là 30/12/2026. Dược liệu chưa nằm trong danh mục EUDR, nhưng người mua ngày càng đòi hỏi bằng chứng tương đương. **Tiền lệ:** HTX Cự Nẫm (Quảng Bình) với cây cà gai leo; Nền tảng VNPT Green QR — hạ tầng đã có sẵn, do đó lợi thế cạnh tranh của Sankit nằm ở chất lượng dữ liệu không gian trong ngách "dưới tán rừng, đồng bào dân tộc thiểu số, môi trường ngoại tuyến (offline)" mà các nền tảng lớn chưa tối ưu.
2. **Giám sát biến động.** Phủ ảnh vệ tinh lên đa giác — sử dụng Sentinel-2 (miễn phí, độ phân giải 10m, chu kỳ quay vòng 5 ngày; chỉ số NDVI để đánh giá sức khỏe cây trồng/rừng) thông qua Google Earth Engine (nâng cấp lên Planet Labs cho các thửa đất nhỏ). Phát hiện tình trạng mất rừng so với mốc cơ sở năm 2020.
3. **Quy hoạch vùng trồng mới (làm sau).** Mô hình hóa mức độ phù hợp của môi trường sống (WorldClim, CHIRPS, SoilGrids) kết hợp với tri thức bản địa về nơi dược liệu mọc hoang, nhằm hướng dẫn việc di thực và giảm thiểu rủi ro trong khoảng thời gian 3–5 năm chuẩn hóa vùng trồng.

#### Điều này giải quyết một phần câu hỏi về chống gian lận (Anti-spoofing)
Điểm số 2 là câu trả lời cụ thể cho rủi ro làm giả GPS/thời gian được nêu trong phần *Rủi ro, Lỗ hổng & Câu hỏi còn ngỏ*: đối chiếu chéo bằng vệ tinh độc lập. Nếu một vùng trồng báo cáo có thu hoạch nhưng ảnh vệ tinh Sentinel-2 không cho thấy hoạt động canh tác tương ứng, hệ thống sẽ gắn cờ để kiểm định viên xem xét. Điều này không giải quyết hoàn toàn vấn đề gian lận, nhưng nó bổ sung một nguồn bằng chứng đối chiếu bên ngoài rất khó làm giả.

### Vì sao vệ tinh khác với siêu dữ liệu ảnh (logic bảo mật)

Dữ liệu vệ tinh không phải là khó can thiệp hơn về mặt kỹ thuật — mà vấn đề là **không có bên nào trong giao dịch kiểm soát được nó**, và đó chính là lý do nó đáng tin cậy:

*   **Siêu dữ liệu (metadata) của ảnh là do tự báo cáo.** GPS + thời gian được tạo ra trên chính điện thoại của nông dân — bên có động cơ để làm tắt. Các ứng dụng giả mạo vị trí có thể làm giả GPS, dữ liệu EXIF có thể bị chỉnh sửa, một bức ảnh cũ có thể được chụp lại. Blockchain không giải quyết được vấn đề này: nó chỉ khóa bản ghi sau khi đã thu thập, do đó một đầu vào giả mạo sẽ chỉ trở thành một "bản giả mạo không thể thay đổi vĩnh viễn" (pitch deck cũng thừa nhận blockchain “không thể tự động làm cho dữ liệu thô trên đồng ruộng trở nên chính xác”).
*   **Vệ tinh là một nhân chứng độc lập.** Vệ tinh Sentinel-2 được vận hành bởi ESA/Copernicus; nông dân không thể chỉnh sửa những gì nó ghi lại, không thể từ chối bị ghi hình và không thể kiểm soát thời điểm nó bay ngang qua.
*   **Bảo mật = đối chiếu chéo giữa hai nguồn độc lập.** Để làm giả một yêu cầu một cách thuyết phục, giờ đây bạn cần phải làm cho lời nói dối trên mặt đất và hình ảnh từ bầu trời khớp với nhau — điều này khó hơn rất nhiều so với việc chỉnh sửa một trường dữ liệu EXIF.

*Lưu ý:* Dữ liệu vệ tinh mang tính chất bổ trợ chứng thực, không phải là bức tranh hoàn chỉnh — độ phân giải ~10m, chu kỳ ~5 ngày, bị cản trở bởi mây, không thể nhìn xuyên qua tán rừng hoặc xác minh các chi tiết nhỏ (như "đã sử dụng phân bón hữu cơ"). Vấn đề chống giả mạo ở cấp độ thiết bị ngay tại thời điểm thu thập dữ liệu vẫn là một bài toán cần giải quyết.

### Dữ liệu vệ tinh có miễn phí không? (Về chi phí)
*   **Ảnh Sentinel-2:** Miễn phí vĩnh viễn (dữ liệu mở của EU Copernicus/ESA; độ phân giải 10m, chu kỳ ~5 ngày). Đây là công cụ chủ lực.
*   **Google Earth Engine (Xử lý):** Miễn phí cho mục đích phi thương mại/học thuật/phi lợi nhuận/nghiên cứu (áp dụng hạn mức điện toán miễn phí hàng tháng từ tháng 4/2026); tư cách pháp nhân đại học của Sankit hoàn toàn đủ điều kiện trong giai đoạn đầu. Việc sử dụng cho mục đích thương mại sẽ tính phí dựa trên báo giá (phí nền tảng hàng tháng + điện toán/lưu trữ), không niêm yết công khai — cần liên hệ Google hoặc đối tác.
*   **Planet Labs (Độ phân giải cao hơn):** Trả phí, chỉ dùng nếu độ phân giải 10m là quá mờ đối với các thửa đất nhỏ. Bản đồ nền (Basemaps) qua dịch vụ "Lens" khoảng $1.999/tháng hoặc $19.999/năm; dịch vụ chụp theo yêu cầu (PlanetScope tasking) định giá theo "Số hecta quản lý" + khu vực (dựa trên báo giá). Có chương trình hỗ trợ nghiên cứu/khoa học miễn phí cho các học giả đủ điều kiện.

**Tóm lại:** Ngăn xếp công nghệ đề xuất bắt đầu với chi phí $0 và chỉ tốn tiền nếu Sankit cần độ phân giải sắc nét hơn của Planet hoặc chuyển sang mô hình thương mại hoàn toàn trên Google Earth Engine.

### Carbon — Hai mô hình

**Mô hình A — Carbon rừng (dưới tán).** Khả thi ngay lập tức. Khung pháp lý rõ ràng nhất (Nghị định 180/2026), phù hợp với định hướng rừng bảo tồn. Có hai dòng doanh thu: (1) dược liệu thông qua chuỗi cung ứng được kiểm soát của Sankit; (2) carbon rừng được đo đạc, thẩm định và bán qua sàn giao dịch/hợp đồng. **Vai trò của GIS:** đa giác + ảnh vệ tinh chuỗi thời gian (trước/sau) là bằng chứng không gian bắt buộc cho MRV (Đo đạc–Báo cáo–Thẩm định), được yêu cầu bởi bất kỳ đơn vị thẩm định nào (nội địa hoặc Verra VCS). **Tiền lệ:** một nông dân người Thái đã giữ lại tán rừng mét/quế và trồng trà hoa vàng có giá trị cao bên dưới. **Thách thức:** theo Nghị định 119/2025, chỉ các tổ chức (chứ không phải hộ gia đình cá nhân) mới được đăng ký dự án carbon — do đó Sankit (hoặc một pháp nhân hợp tác xã/doanh nghiệp) phải là bên đứng ra đăng ký, với các hộ gia đình là bên thụ hưởng theo một thỏa thuận chia sẻ lợi ích minh bạch.

**Mô hình B — Carbon nông nghiệp (canh tác bền vững).** Khó hơn / để thực hiện sau. Hiện chưa có phương pháp luận quốc gia cho việc canh tác dược liệu; phải dựa vào các tiêu chuẩn quốc tế (Verra VM0042, Gold Standard) với chi phí đo đạc/thẩm định cao; mức độ hấp thụ carbon trên mỗi hecta thấp hơn rất nhiều so với rừng. Hiện tại, nên sử dụng mô hình này như một câu chuyện về ESG/marketing ("canh tác phát thải thấp") hơn là một dòng doanh thu độc lập.

#### Khuyến nghị (Ưu tiên tính khả thi pháp lý)
*   **Ngắn hạn (1–2 năm):** Thí điểm carbon rừng trên 1–2 vùng trồng dưới tán có dữ liệu được ghi chép đầy đủ nhất, phối hợp với một đơn vị thẩm định có kinh nghiệm để tìm hiểu thực tế về quy trình MRV theo Nghị định 180/2026. Song song đó: xây dựng bộ hồ sơ ESG "canh tác phát thải thấp" cho các vùng trồng còn lại.
*   **Trung hạn (3–5 năm):** Mở rộng sang carbon nông nghiệp nếu nhà nước ban hành phương pháp luận quốc gia cho dược liệu/nông lâm kết hợp — cần theo dõi sát sao, vì chính sách đang thay đổi rất nhanh (có hơn 5 nghị định mới trong nửa đầu năm 2026).

### Kiến trúc dữ liệu 4 lớp dùng chung

Cần thiết kế dùng chung ngay từ đầu để mỗi chuyến đi thực địa tốn kém có thể phục vụ cả ba tác vụ GIS + carbon, thay vì phải đi ba chuyến riêng biệt:

1. **Đa giác vùng trồng (Plot polygon)** — thu thập một lần ngoại tuyến (offline); làm khóa chính (Plot ID).
2. **Hồ sơ canh tác & thu hoạch** — phục vụ truy xuất nguồn gốc và làm dữ liệu hoạt động cho tín chỉ carbon.
3. **Ảnh vệ tinh chuỗi thời gian** — giám sát biến động và làm bằng chứng MRV cho carbon rừng.
4. **Dữ liệu khí hậu/thổ nhưỡng** — nền tảng tĩnh để quy hoạch vùng trồng mới + ước tính tiềm năng carbon.

### Ngăn xếp công nghệ đề xuất (Tham khảo)

Thu thập dữ liệu thực địa ngoại tuyến (app tự phát triển, tham khảo KoBoToolbox/ODK Collect, Mapeo) · Lưu trữ PostGIS (hoặc Mapbox/ArcGIS Online) · Sentinel-2 qua Google Earth Engine (→ Planet Labs khi cần) · API kết nối hệ thống truy xuất quốc gia · MRV thông qua một đơn vị thẩm định carbon rừng có kinh nghiệm tại Việt Nam (tham khảo tiêu chuẩn Verra VCS cho các bộ hồ sơ thị trường tự nguyện song song).

### Lộ trình 

| Giai đoạn | Thời gian | Trọng tâm | Mục tiêu kỳ vọng |
| :--- | :--- | :--- | :--- |
| 1 | 0–6 tháng | Module đa giác ngoại tuyến + hồ sơ canh tác; Plot ID tương thích với hệ thống quốc gia | 100% vùng trồng hiện tại được số hóa |
| 2 | 6–12 tháng | Sentinel-2 qua GEE; AI đối chiếu chéo các báo cáo với hình ảnh vệ tinh | Cảnh báo sớm về tình trạng mất rừng; giảm thiểu chi phí kiểm tra thực địa |
| 3 | 12–18 tháng | Thí điểm carbon rừng trên 1–2 vùng trồng dưới tán; hợp tác với đơn vị thẩm định | Nộp hồ sơ dự án carbon đầu tiên theo Nghị định 180/2026 |
| 4 | 18–24 tháng | Tích hợp lớp dữ liệu khí hậu/thổ nhưỡng để quy hoạch vùng trồng mới | Tạo bản đồ vùng trồng mới có cơ sở khoa học |
| 5 | 24+ tháng | Đánh giá chương trình thí điểm; cân nhắc triển khai carbon nông nghiệp | Vận hành song song hai dòng doanh thu (dược liệu + carbon) |

### Rủi ro đặc thù của Carbon

*   **Chính sách thay đổi rất nhanh** (hơn 5 văn bản lớn trong nửa đầu năm 2026) — cần giữ cho mô hình dữ liệu linh hoạt, không nên gắn cứng với một phương pháp luận duy nhất.
*   **Quyền sở hữu carbon** trên đất rừng cộng đồng/đồng bào dân tộc thiểu số phải được làm rõ bằng các hợp đồng minh bạch trước khi triển khai.
*   **Chi phí thẩm định của bên thứ ba** đối với các thửa đất nhỏ là rất cao — cần gộp các vùng liền kề thành một dự án chung để chia sẻ chi phí này.
*   **Giới hạn xuất khẩu 50%** đối với tín chỉ carbon rừng (theo Nghị định 180/2026) phải được đưa vào mô hình tài chính ngay từ đầu.
