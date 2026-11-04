# HKICO Python: บทเรียนแบบทดลองโค้ด

สื่อการสอนเตรียมสอบ **Hong Kong International Computational Olympiad (HKICO), Heat Round, Python**
ทุกบทเรียนเป็น notebook ที่เปิดใน Google Colab ได้ทันที ไม่ต้องติดตั้งโปรแกรมอะไร

| คาบ | วันที่ | เนื้อหา | เปิด |
|---|---|---|---|
| 1 | 7 พ.ย. 2026 | Mock Paper 1 (20 ข้อ) + กลยุทธ์ทำข้อสอบ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Cpongrawee/hkico-python-lessons/blob/main/notebooks/mock1_lesson.ipynb) |

---

## 👩‍🎓 สำหรับนักเรียน

1. กดปุ่ม **Open in Colab** ของคาบนั้น
2. ล็อกอินบัญชี Google ของตัวเอง
3. กด **File → Save a copy in Drive** เพื่อให้มีไฟล์ของตัวเอง คำตอบที่พิมพ์จะได้ถูกบันทึกไว้
4. ห้ามเปิดหัวข้อ **✅ เฉลย** จนกว่าครูจะบอก 🙈

---

## 👩‍🏫 สำหรับครู: ใช้บนคอมพิวเตอร์ของโรงเรียน

### ✅ ซ้อมก่อนวันสอน (5 นาที ทำบนคอมพิวเตอร์ของโรงเรียนถ้าทำได้)
- [ ] เปิดหน้านี้ แล้วกด **Open in Colab**
- [ ] ล็อกอิน Google แล้วรัน cell `print(__name__)` ในข้อ 1 ต้องได้ `__main__`
- [ ] รัน `%%writefile greet.py` และ `!python greet.py` ในข้อ 1 ได้ไม่มี error
- [ ] เปิดลิงก์ **Python Tutor** ของข้อ 15 แล้วกด Next ได้
- [ ] ลองแชร์หน้าจอหรือขึ้นโปรเจกเตอร์ แล้วเช็คว่าตัวอักษรใหญ่พอ (กด `Ctrl` + `+` เพื่อขยาย)

### 🛟 แผนสำรอง
| ปัญหา | ทางแก้ |
|---|---|
| ล็อกอิน Google ไม่ได้ | Colab ยังเปิดดูได้แต่รันไม่ได้ → ใช้ลิงก์ Python Tutor ใน notebook รันโค้ดแทน (ไม่ต้องล็อกอิน) |
| เครือข่ายของโรงเรียนบล็อก Colab | เปิดไฟล์ notebook บน GitHub (กดที่ไฟล์ใน `notebooks/`) เพื่ออ่านเนื้อหา แล้วใช้ Python Tutor รันโค้ด |
| บล็อกทั้งหมด | ใช้ hotspot จากมือถือ |

### 🔒 ความปลอดภัยบนคอมพิวเตอร์ที่ใช้ร่วมกัน
- ล็อกอิน Google ใน **หน้าต่าง Incognito / InPrivate** (`Ctrl` + `Shift` + `N`)
- อย่ากด "จดจำรหัสผ่าน"
- สอนเสร็จแล้ว **ปิดหน้าต่าง Incognito ทั้งหมด** บัญชีจะถูกล็อกเอาต์อัตโนมัติ

### 📤 แชร์ให้นักเรียนตอนเริ่มคาบ
ส่งลิงก์ของหน้านี้ หรือลิงก์ Colab โดยตรง:
```
https://colab.research.google.com/github/Cpongrawee/hkico-python-lessons/blob/main/notebooks/mock1_lesson.ipynb
```

> ⚠️ ถ้าแก้ notebook ใน Colab การแก้ไขจะ **ไม่ถูกบันทึกกลับขึ้น GitHub** อัตโนมัติ ถ้าต้องการบันทึก ให้กด File → Save a copy in GitHub
