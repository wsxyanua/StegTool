# STEGANOGRAPHY v1.0 — HƯỚNG DẪN SỬ DỤNG

## TỔNG QUAN

Steganography v1.0 là một công cụ để giấu thông điệp bí mật vào ảnh, dành cho khi mã hóa thông thường có vẻ chưa đủ trình. Ứng dụng có cả bản web và phần mềm desktop để tiện dùng ở nhiều tình huống.

## ỨNG DỤNG WEB

### BẮT ĐẦU

1. Mở `web/index.html` bằng trình duyệt.
2. Chọn tab HIDE (Giấu) hoặc EXTRACT tabs (Trích xuất).
3. Chọn phương pháp steganography: LSB cho người mới, DCT/DWT cho người muốn nâng cao.

### GIẤU THÔNG ĐIỆP

1. **Chọn file**: Bấm để chọn ảnh PNG/BMP/TIFF.
2. **Nhập thông điệp**: Gõ nội dung bí mật vào ô văn bản.
3. **Đặt mật khẩu**: Tùy chọn — nếu muốn mã hóa trước khi giấu.
4. **Chọn phương pháp**: 
   - LSB: phương pháp cơ bản, dung lượng tốt.
   - DCT: thao tác ở miền tần số, bền hơn trước biến đổi.
   - DWT: miền sóng con (wavelet), kỹ thuật nâng cao.
5. **Generate Signature**: tùy chọn tạo chữ ký số để xác thực.
6. **Hide Message**: bấm để xử lý và tải ảnh kết quả về.

### TRÍCH XUẤT THÔNG ĐIỆP

1. **Chọn file**: Cchọn ảnh chứa thông điệp đã giấu.
2. **Nhập mật khẩu**: nếu thông điệp đã được mã hóa.
3. **Chọn phương pháp**: phải khớp với phương pháp đã dùng lúc giấu.
4. **Trích xuất**: bấm để hiển thị nội dung ẩn.
5. **Xác thực chữ ký**: tuỳ chọn kiểm tra chữ ký số.

### STEGANOGRAPHY ÂM THANH

1. **Định dạng hỗ trợ**: MP3, WAV, FLAC
2. **Phương pháp có sẵn**:
   - LSB: giấu vào bit mẫu âm thanh.
   - Phase: điều chỉnh pha tần số.
   - Echo: dùng độ trễ echo để mã hoá.
3. **Quy trình**: tương tự như steganography trên ảnh.

### QUẢN LÝ CÀI ĐẶT

- **Export Settings**: lưu bản sao cấu hình đã mã hóa.
- **Import Settings**: phục hồi từ file sao lưu.
- **Theme Toggle**: chuyển giữa giao diện sáng/tối.

## ỨNG DỤNG DESKTOP

### CÀI ĐẶT

1. Tải `main.py` và các thư viện phụ thuộc.
2. Cài Python 3.7+ cùng PIL và numpy. (phiên bản python mới nhất cũng được)
3. Chạy: `python main.py`

### TÍNH NĂNG

- **Recent Files**: truy cập nhanh các ảnh đã dùng gần đây.
- **Settings Export/Import**: sao lưu và phục hồi tuỳ chọn.
- **Portable Mode**: lưu cấu hình trong thư mục ứng dụng (dễ mang theo).
- **Giao diện chuyên nghiệp**: thiết kế gọn gàng, hiện đại.

### QUY TRÌNH GIẤU

1. **File Menu**: mở ảnh hoặc chọn từ danh sách recent.
2. **Hide Tab**: nhập thông điệp và mật khẩu (nếu cần).
3. **Capacity Display**: hiển thị dung lượng tối đa có thể chứa.
4. **Character Counter**: đếm ký tự theo thời gian thực.
5. **Save Result**: chọn nơi lưu ảnh stego.

### QUY TRÌNH TRÍCH XUẤT

1. **Extract Tab**: chọn ảnh chứa thông điệp.
2. **Password**: nhập nếu thông điệp đã mã hóa.
3. **View Result**: nội dung trích xuất hiển thị trong ô văn bản.

## ĐỊNH DẠNG HỖ TRỢ

### ẢNH
- **PNG**: khuyến nghị để giữ chất lượng tốt nhất.
- **BMP**: không nén, đáng tin cậy.
- **TIFF**: định dạng chuyên nghiệp.
- **JPEG**: sẽ tự động chuyển sang PNG trước khi giấu.

### ÂM THANH
- **WAV**: không nén, chất lượng tốt nhất.
- **MP3**: hỗ trợ nén.
- **FLAC**: nén không mất dữ liệu.

## TÍNH NĂNG BẢO MẬT

### MÃ HÓA
- **AES-256**: mã hóa mức mạnh.
- **PBKDF2**: hàm dẫn xuất khóa.
- **Salt**: muối ngẫu nhiên cho mỗi lần mã hóa.

### CHỮ KÝ SỐ
- **RSA**: mật mã khóa công khai.
- **Sinh khóa**: tự động tạo cặp khóa.
- **Xác minh**: kiểm tra tính xác thực.

### QUYỀN RIÊNG TƯ
- **Xử lý phía client**: toàn bộ xử lý diễn ra trong trình duyệt.
- **Không upload**: file không rời khỏi thiết bị của bạn.
- **Portable**: ứng dụng desktop lưu cấu hình cục bộ.

## KHUYẾN NGHỊ TỐT NHẤT

### KHI GIẤU THÔNG ĐIỆP
1. Dùng định dạng PNG để đạt kết quả tốt nhất.
2. Chọn mật khẩu mạnh (từ 12 ký tự trở lên).
3. Giữ thông điệp dưới 80% dung lượng tối đa.
4. Dùng DCT/DWT cho thông điệp quan trọng.

### VỀ BẢO MẬT
1. Luôn mã hóa khi chứa dữ liệu nhạy cảm.
2. Tạo chữ ký số để xác thực nguồn.
3. Kiểm tra kỹ nội dung đã trích xuất.
4. Lưu bản sao ảnh gốc để sao lưu.

### QUẢN LÝ FILE
1. Giữ ảnh gốc riêng biệt.
2. Dùng tên file mô tả.
3. Thường xuyên xuất cài đặt (backup).
4. Xóa recent files khi cần bảo mật.

## KHẮC PHỤC SỰ CỐ

### VẤN ĐỀ THƯỜNG GẶP

**Thông điệp quá dài**
- Kiểm tra hiển thị dung lượng.
- Rút ngắn thông điệp.
- Dùng ảnh có kích thước lớn hơn.

**Trích xuất thất bại**
- Đảm bảo mật khẩu đúng.
- Kiểm tra phương pháp steganography sử dụng.
- Đảm bảo ảnh chưa bị chỉnh sửa sau khi giấu.

**File không được hỗ trợ**
- Chuyển JPEG thành PNG.
- Dùng định dạng không nén.
- Kiểm tra file có bị hỏng không.

**Vấn đề trình duyệt**
- Dùng trình duyệt hiện đại.
- Bật JavaScript.
- Kiểm tra giới hạn kích thước file.

### THÔNG BÁO LỖI

**"No hidden message found"**
- Phương pháp trích xuất sai.
- Ảnh không chứa thông điệp.
- File bị chỉnh sửa sau khi giấu.

**"Password required"**
- Tin nhắn đã được mã hóa
- Nhập đúng mật khẩu
- Kiểm tra mật khẩu có chữ cái hoa hay thường

**"Invalid file format"**
- Chỉ dùng định dạng được hỗ trợ.
- Kiểm tra phần mở rộng file.
- Xác minh tính toàn vẹn file.

## CHI TIẾT KỸ THUẬT

### THUẬT TOÁN
- **LSB**: thay thế Least Significant Bit (bit ít nghĩa nhất).
- **DCT**: miền biến đổi cos rời rạc.
- **DWT**: miền biến đổi wavelet.

### TÍNH TOÁN DUNG LƯỢNG
- LSB: ChiềuRộng × ChiềuCao × SốKênh ÷ 8 (ký tự).
- DCT: xấp xỉ 60% dung lượng LSB.
- DWT: xấp xỉ 40% dung lượng LSB.

### HIỆU NĂNG
- **Web**: xử lý phía client, không cần server.
- **Desktop**: hiệu năng native, hỗ trợ file lớn hơn.
- **Memory**: huật toán hiệu quả, tiêu thụ RAM ở mức tối thiểu hợp lí.

## HỖ TRỢ

Nếu gặp vấn đề hoặc có câu hỏi:
1. Đầu tiên đọc kỹ hướng dẫn này.
2. Xem lại thông báo lỗi để biết chi tiết.
3. Kiểm tra định dạng và kích thước file.
4. Thử với thông điệp đơn giản trước.

KHÔNG ĐƯỢC NỮA THÌ HỎI THẰNG CODE.
