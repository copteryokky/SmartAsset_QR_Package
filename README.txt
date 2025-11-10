Smart Asset — QR Pages Builder

ไฟล์สำคัญ
- build_pages_and_qr.py   (สคริปต์หลัก)
- Smart Asset Lab.xlsx    (ไฟล์ข้อมูล Excel — แผ่นแรก)
- pages/                  (ผลลัพธ์หน้า HTML ต่อรายการ + index.html)
- qrcodes/                (รูป PNG QR รายการละไฟล์)
- qr_labels_A4_pages.pdf  (รวม QR เป็น A4 3x8 สำหรับพิมพ์)

วิธีใช้งาน (รันบนเครื่องคุณ)
1) ติดตั้งไลบรารี:
   pip install pandas openpyxl "qrcode[pil]" reportlab Pillow
2) วางสคริปต์และไฟล์ Excel ไว้โฟลเดอร์เดียวกัน
3) เปิดไฟล์ build_pages_and_qr.py แล้วแก้ BASE_URL ให้เป็น URL จริงของโฟลเดอร์ pages บนโฮสต์ของคุณ
   เช่น BASE_URL = "https://hms.example.org/asset/pages/"
4) รัน:
   python build_pages_and_qr.py
5) อัปโหลดโฟลเดอร์ pages ไปยังโฮสต์ แล้วพิมพ์สติ๊กเกอร์จาก qr_labels_A4_pages.pdf

หมายเหตุ:
- ค่า field จะแสดงตามคอลัมน์ใน Excel โดยจัดลำดับคอลัมน์ยอดนิยมไว้ด้านบน
- ถ้าต้องการฟิลด์/ลำดับเฉพาะ ปรับลิสต์ 'prefer' ในสคริปต์
