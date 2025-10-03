# คู่มือคำจำกัดความและเกณฑ์การให้คะแนนตำแหน่ง IT Manager

**เอกสารอ้างอิง:** it_manager_scoring_md.md, job_announcement.md  
**วันที่จัดทำ:** 2025-09-30  
**วัตถุประสงค์:** กำหนดคำจำกัดความที่ชัดเจนเพื่อป้องกันความสับสนในการประเมินผู้สมัคร

---

## 1. คำจำกัดความของ "คะแนน" (Score)

### ⚠️ สำคัญมาก: มีคะแนน 3 ประเภทที่แตกต่างกัน

### 1.1 Performance Rating (คะแนนประเมินผลงาน)
- **คำอธิบาย:** คะแนนจากการประเมินผลการปฏิบัติงานประจำปี
- **แหล่งข้อมูล:** ตาราง `performance_reviews.overall_score`
- **Scale:** 1.0 - 5.0
- **การแปลงเป็นเปอร์เซ็นต์:** (overall_score / 5.0) × 100
- **ตัวอย่าง:** 
  - 4.2 / 5.0 = 84%
  - 4.5 / 5.0 = 90%
- **การใช้งาน:** ใช้ประเมินผลงานประจำปี ไม่ใช่เกณฑ์คัดเลือก IT Manager โดยตรง
- **⚠️ คำเตือน:** **Performance Rating ≠ Total Selection Score**

---

### 1.2 Basic Qualification Score (คะแนนคุณสมบัติพื้นฐาน)
- **คำอธิบาย:** การตรวจสอบคุณสมบัติพื้นฐาน 11 ข้อตามประกาศตำแหน่ง
- **น้ำหนัก:** 30% ของคะแนนรวม
- **กฎการให้คะแนน:**
  - ✅ ผ่านทุกข้อ (11/11) → ได้ 30%
  - ❌ ขาดแม้เพียง 1 ข้อ → ได้ 0%
  - **ไม่มีคะแนนบางส่วน (partial credit)**

#### รายการคุณสมบัติพื้นฐาน 11 ข้อ:

| # | คุณสมบัติ | เกณฑ์ | ตาราง/ฟิลด์ |
|---|-----------|-------|-------------|
| 1 | วุฒิการศึกษา | ≥ ปริญญาโท (Master's) | `education.degree_level` |
| 2 | อายุงาน | ≥ 5 ปี | `employees.hire_date` |
| 3 | Java Programming | ระดับ "เชี่ยวชาญ" (Expert) | `skills.proficiency_level` |
| 4 | System Analysis | ระดับ "ชำนาญ" (Proficient) | `skills.proficiency_level` |
| 5 | Project Management | ระดับ "ปานกลาง" (Intermediate) ขึ้นไป | `skills.proficiency_level` |
| 6 | ใบรับรอง | Oracle Certified Professional (ยังไม่หมดอายุ) | `certifications.certificate_name` |
| 7 | คะแนนประเมินผลงาน | ≥ 4.0 / 5.0 | `performance_reviews.overall_score` |
| 8 | ประสบการณ์ ERP | มีประสบการณ์ระบบ ERP หรือระบบขนาดใหญ่ | `projects.project_name` LIKE '%ERP%' |
| 9 | ภาษาอังกฤษ | ระดับ "ดี" (Good) | `employees.english_proficiency` |
| 10 | ประสบการณ์ผู้นำ | มีประสบการณ์นำทีม | `position_history.position_name` LIKE '%หัวหน้า%' |
| 11 | สถานะพนักงาน | Permanent (ประจำ) | `employees.employee_type` = 'Permanent' |

**ตัวอย่าง SQL:**
```sql
CASE 
  WHEN (เงื่อนไข_ทั้ง_11_ข้อ_เป็นจริง) THEN 30
  ELSE 0
END AS basic_qualification_score
```

---

### 1.3 Total Selection Score (คะแนนรวมสำหรับการคัดเลือก)
- **คำอธิบาย:** คะแนนรวมจาก 3 ส่วนสำหรับคัดเลือก IT Manager
- **โครงสร้าง:**
  ```
  Total Selection Score = ส่วน 1 + ส่วน 2 + ส่วน 3
  ```

#### ส่วนที่ 1: Basic Qualification (30%)
- ตรวจสอบคุณสมบัติพื้นฐาน 11 ข้อ
- ได้ 30% หรือ 0% เท่านั้น

#### ส่วนที่ 2: Knowledge Test (30%)
- คะแนนการทดสอบความรู้ (0-100 คะแนน)
- การคำนวณ: `(test_score / 100) × 30%`
- **แหล่งข้อมูล:** ตาราง `it_manager_tests` (หากมี)
- ตัวอย่าง:
  - คะแนนสอบ 80/100 → 0.80 × 30% = 24%
  - คะแนนสอบ 90/100 → 0.90 × 30% = 27%

#### ส่วนที่ 3: Interview (40%)
- คะแนนการสัมภาษณ์ (0-100 คะแนน)
- การคำนวณ: `(interview_score / 100) × 40%`
- **แหล่งข้อมูล:** ตาราง `it_manager_interviews` (หากมี)
- ตัวอย่าง:
  - คะแนนสัมภาษณ์ 70/100 → 0.70 × 40% = 28%
  - คะแนนสัมภาษณ์ 85/100 → 0.85 × 40% = 34%

**สูตรคำนวณ:**
```sql
total_selection_score = 
  basic_qualification_score +  -- 0% หรือ 30%
  (test_score / 100 × 30) +    -- 0-30%
  (interview_score / 100 × 40) -- 0-40%
```

---

## 2. ข้อจำกัดสำคัญของคะแนน

### 2.1 คะแนนสูงสุดที่เป็นไปได้

| สถานการณ์ | Basic (30%) | Test (30%) | Interview (40%) | Total | สรุป |
|-----------|-------------|------------|-----------------|-------|------|
| ผ่านทุกข้อ + เต็มทุกส่วน | 30% | 30% | 40% | **100%** | สูงสุด |
| **ไม่ผ่าน basic** + เต็มทุกส่วน | **0%** | 30% | 40% | **70%** | ⚠️ สูงสุด |
| ผ่านทุกข้อ + เต็ม test เท่านั้น | 30% | 30% | 0% | 60% | ไม่แนะนำ |

### 2.2 กฎสำคัญ

```
⚠️ ถ้า basic_pass = 0 (ไม่ผ่านคุณสมบัติพื้นฐาน)
→ คะแนนรวมสูงสุด = 70%
→ ไม่สามารถได้คะแนนรวม > 80% ได้
```

**ผลกระทบ:**
- การค้นหา "พนักงานที่คะแนนรวม > 80% แต่ไม่ผ่านคุณสมบัติพื้นฐาน" → **logically impossible**
- ต้องผ่านคุณสมบัติพื้นฐานก่อน จึงจะมีโอกาสได้คะแนนรวม > 80%

---

## 3. คำศัพท์ที่ใช้บ่อย

### 3.1 "ศักยภาพสูง" (High Potential)
**คำจำกัดความ 1 (ตาม Performance Rating):**
- Performance Rating ≥ 4.0 / 5.0 (80%)
- **ไม่ได้หมายถึง** Total Selection Score > 80%

**คำจำกัดความ 2 (ตามบริบท HR):**
- พนักงานที่มีแนวโน้มพัฒนาสู่ตำแหน่งที่สูงขึ้น
- อาจพิจารณาจากหลายปัจจัย: performance, potential rating, leadership quality

**⚠️ คำแนะนำ:** ระบุให้ชัดเจนว่าหมายถึงคะแนนแบบไหน

---

### 3.2 "ไม่ผ่านเกณฑ์" / "ขาดคุณสมบัติ"

**ความหมายที่ 1: ไม่ผ่านคุณสมบัติพื้นฐาน (Basic Qualification)**
- ขาดอย่างน้อย 1 ใน 11 ข้อ
- ได้คะแนนส่วน 1 = 0%
- ตัวอย่าง: ไม่มีป.โท, อายุงานไม่ครบ 5 ปี

**ความหมายที่ 2: ขาดคุณสมบัติเพิ่มเติม (Additional Requirements)**
- ผ่านคุณสมบัติพื้นฐาน 11 ข้อแล้ว
- แต่ขาดทักษะ/ใบรับรองอื่นที่จำเป็นสำหรับความสำเร็จในงาน
- ตัวอย่าง: ไม่มีใบรับรอง ITIL, ไม่มีประสบการณ์บริหารงบประมาณ

**⚠️ คำแนะนำ:** ระบุให้ชัดว่าหมายถึงความหมายไหน

---

### 3.3 "คะแนนเกิน 80%" - ต้องระบุให้ชัดเจน!

**❌ ไม่ชัดเจน:**
```
"หาพนักงานที่คะแนนเกิน 80%"
```

**✅ ชัดเจน:**
```
"หาพนักงานที่ Total Selection Score > 80%"
หรือ
"หาพนักงานที่ Performance Rating > 4.0/5.0 (80%)"
```

---

## 4. ตัวอย่างการใช้งาน

### 4.1 Query ที่ถูกต้อง

**ตัวอย่าง 1: หาพนักงานที่มี Performance Rating สูง แต่ยังขาดคุณสมบัติพื้นฐาน**

```sql
-- High performance but not qualified for IT Manager
WITH performance AS (
  SELECT employee_id, 
         overall_score,
         overall_score / 5.0 AS performance_pct
  FROM performance_reviews
  WHERE overall_score >= 4.0  -- Performance Rating >= 80%
),
basic_qual AS (
  SELECT employee_id,
         CASE WHEN [ครบ_ทั้ง_11_ข้อ] THEN 1 ELSE 0 END AS qualified
  FROM employees e
  LEFT JOIN education ed ON ...
  LEFT JOIN skills s ON ...
  -- ... เช็คทั้ง 11 ข้อ
)
SELECT p.employee_id,
       e.first_name,
       e.last_name,
       p.performance_pct,
       bq.qualified
FROM performance p
JOIN basic_qual bq ON p.employee_id = bq.employee_id
JOIN employees e ON p.employee_id = e.employee_id
WHERE bq.qualified = 0;  -- ไม่ผ่านคุณสมบัติพื้นฐาน
```

**ตัวอย่าง 2: คำนวณ Total Selection Score (ถ้ามีข้อมูลครบ)**

```sql
WITH scores AS (
  SELECT e.employee_id,
         -- ส่วน 1: Basic Qualification (30%)
         CASE WHEN [ครบ_11_ข้อ] THEN 30 ELSE 0 END AS basic_score,
         -- ส่วน 2: Knowledge Test (30%)
         COALESCE(t.test_score / 100.0 * 30, 0) AS test_score,
         -- ส่วน 3: Interview (40%)
         COALESCE(i.interview_score / 100.0 * 40, 0) AS interview_score
  FROM employees e
  LEFT JOIN it_manager_tests t ON e.employee_id = t.employee_id
  LEFT JOIN it_manager_interviews i ON e.employee_id = i.employee_id
  -- ... joins สำหรับเช็ค basic qualification
)
SELECT employee_id,
       basic_score,
       test_score,
       interview_score,
       (basic_score + test_score + interview_score) AS total_selection_score
FROM scores
WHERE (basic_score + test_score + interview_score) > 80;
```

---

### 4.2 Query ที่ไม่สามารถหาผลได้ (Logically Impossible)

**ตัวอย่าง: หา Total Selection Score > 80% แต่ basic_pass = 0**

```sql
-- ⚠️ Query นี้จะได้ผลลัพธ์ว่าง (0 rows) เสมอ
SELECT *
FROM (
  SELECT employee_id,
         CASE WHEN [ครบ_11_ข้อ] THEN 30 ELSE 0 END AS basic_score,
         [คำนวณ_test_และ_interview]
  FROM ...
) scores
WHERE basic_score = 0  -- ไม่ผ่าน basic
  AND (basic_score + test_score + interview_score) > 80;  -- เป็นไปไม่ได้!
```

**เหตุผล:**
```
basic_score = 0
test_score ≤ 30
interview_score ≤ 40
-----------------
total_score ≤ 70  → ไม่สามารถ > 80 ได้
```

---

## 5. Checklist สำหรับการ Query

ก่อนสร้าง query ให้ตรวจสอบ:

- [ ] ระบุชัดว่าต้องการคะแนนแบบไหน?
  - [ ] Performance Rating (4.0/5.0)?
  - [ ] Basic Qualification Score (0% หรือ 30%)?
  - [ ] Total Selection Score (0-100%)?

- [ ] ถ้าต้องการ Total Selection Score:
  - [ ] มีตาราง `it_manager_tests` หรือไม่?
  - [ ] มีตาราง `it_manager_interviews` หรือไม่?
  - [ ] ถ้าไม่มี → ไม่สามารถคำนวณได้ครบถ้วน

- [ ] ตรวจสอบ logic:
  - [ ] ถ้า basic_pass = 0 และต้องการ total > 80% → impossible
  - [ ] ถ้า basic_pass = 1 และต้องการหา "ไม่ผ่านเกณฑ์" → contradictory

---

## 6. FAQ

### Q1: "พนักงานที่มีคะแนนสูง (>80%) แต่ขาดคุณสมบัติ" หมายความว่าอย่างไร?

**A:** มี 2 ความหมายที่เป็นไปได้:

1. **Performance Rating > 80% แต่ไม่ผ่าน Basic Qualification:**
   - มี Performance Rating ≥ 4.0/5.0
   - แต่ขาด 1 หรือหลายข้อใน 11 คุณสมบัติพื้นฐาน
   - **นี่เป็นไปได้และมีประโยชน์** → หาคนที่มีศักยภาพเพื่อพัฒนา

2. **Total Selection Score > 80% แต่ไม่ผ่าน Basic Qualification:**
   - **เป็นไปไม่ได้** (logically impossible)
   - เพราะ basic_pass = 0 → total ≤ 70%

**คำแนะนำ:** ระบุให้ชัดว่าต้องการความหมายที่ 1 หรือ 2

---

### Q2: ถ้าไม่มีตาราง test/interview จะคำนวณ Total Selection Score ได้ไหม?

**A:** ไม่ได้อย่างสมบูรณ์

**ทางเลือก:**
1. คำนวณเฉพาะส่วนที่มีข้อมูล (partial score)
2. สมมติค่าเริ่มต้น (แต่ต้องระบุให้ชัดเจน)
3. แจ้งว่าข้อมูลไม่ครบ ไม่สามารถคำนวณได้

**ตัวอย่าง:**
```sql
-- Partial calculation (ถ้าไม่มี test/interview)
SELECT employee_id,
       CASE WHEN [basic_qual] THEN 30 ELSE 0 END AS basic_score,
       'N/A - missing test data' AS test_score,
       'N/A - missing interview data' AS interview_score,
       'Cannot calculate total (missing data)' AS note
FROM ...
```

---

### Q3: สมชาย ใจดี มีคะแนนเท่าไร?

**A:** ขึ้นอยู่กับว่าถามเรื่องคะแนนแบบไหน:

**Performance Rating:**
- `overall_score = 4.2 / 5.0 = 84%`
- อยู่ในระดับ "High Performance"

**Basic Qualification:**
- ต้องตรวจสอบทั้ง 11 ข้อ
- ถ้าผ่านครบ → 30%
- ถ้าขาดแม้ 1 ข้อ → 0%

**Total Selection Score:**
- ต้องมีข้อมูล test + interview
- ถ้าไม่มี → ไม่สามารถคำนวณได้

---

## 7. สรุป

### ข้อควรจำ:
1. มีคะแนน 3 แบบ - ต้องแยกให้ชัด
2. Basic Qualification เป็น "gate-keeper" - ต้องผ่านก่อนจึงจะได้ Total > 80%
3. ถ้าไม่มีข้อมูล test/interview → ไม่สามารถคำนวณ Total Selection Score ได้
4. ระบุคำจำกัดความให้ชัดเจนก่อนสร้าง query

### เอกสารอ้างอิง:
- `job_announcement.md` - คุณสมบัติพื้นฐาน
- `it_manager_scoring_md.md` - สูตรการคำนวณคะแนน

---

**หมายเหตุ:** เอกสารนี้จัดทำเพื่อลดความสับสนและเพิ่ม consistency ในการประเมินผู้สมัครตำแหน่ง IT Manager

**ผู้จัดทำ:** HR Analytics Team  
**วันที่อัปเดตล่าสุด:** 2025-09-30
