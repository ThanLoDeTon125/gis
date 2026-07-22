# Framework Triển khai 5ha tại Song Khủa (Sơn La) - VieTrap

## 1. Mục tiêu Dự án
Bắt đầu thử nghiệm framework cho diện tích **5ha tại Song Khủa, Sơn La** phối hợp với tập đoàn VieTrap.
Mục tiêu cốt lõi: **Đo đạc và đối soát sự đáp ứng giữa tri thức nghiên cứu khoa học với thực tiễn canh tác tại hiện trường.**

## 2. Các thành phần của Framework

### 2.1. Lớp Thu thập Dữ liệu Hiện trường (Data Collection)
- **Công cụ:** Ứng dụng di động thiết kế theo chuẩn **Offline-first mobile simple** dành cho nông dân dân tộc thiểu số.
- **Nội dung:** Ghi nhận nhật ký canh tác thường ngày, quá trình sinh trưởng của cây dược liệu, điều kiện thời tiết, thổ nhưỡng.
- **Mục đích:** Chuyển đổi thói quen ghi chép, số hóa dữ liệu ngay tại nguồn, tránh tình trạng phân mảnh thông tin.

### 2.2. Lớp Giám sát & Xử lý AI (AI Monitoring)
- **Kiểm soát dữ liệu:** Ứng dụng AI phân tích các bản ghi dữ liệu tải lên.
- **Phát hiện bất thường:** Tự động đánh dấu (flag) các trường hợp thiếu dữ liệu (missing data) hoặc có dấu hiệu cố tình làm giả dữ liệu (GPS, thời gian, hình ảnh không khớp).

### 2.3. Lớp Đối soát & Tham chiếu Chuỗi cung ứng (End-to-End Verification)
- Cung cấp cổng truy cập (phân quyền tài khoản) cho các bên thứ ba (kiểm định, kiểm nghiệm y tế, tổ chức chứng nhận).
- Đối soát theo tiêu chuẩn: GACP-WHO và Dược điển V.
- Chứng minh nguồn gốc và chất lượng cho các loại dược liệu quý mọc hoang dã / bán hoang dã được trồng có chủ đích.

## 3. Lộ trình Triển khai (Đề xuất)
1. **Khảo sát vi mô (Micro-GIS):** Lập bản đồ địa hình vi mô 5ha, phân tích điều kiện tiểu khí hậu, chất đất tại Song Khủa.
2. **Triển khai App Offline-first:** Đào tạo tập huấn cho người dân sử dụng ứng dụng di động, phát thiết bị (nếu cần).
3. **Thu thập dữ liệu chu kỳ đầu:** Theo dõi quy trình di thực và trồng mới.
4. **Tham chiếu End-to-end:** Mời các đơn vị kiểm định vào đánh giá giai đoạn 1, chấm điểm sự tuân thủ quy trình.
