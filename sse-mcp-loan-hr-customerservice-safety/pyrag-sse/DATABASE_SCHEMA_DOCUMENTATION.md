# Safety Management Database Schema Documentation

## Database Overview
ระบบฐานข้อมูลสำหรับจัดการความปลอดภัยในโรงงานผลิตเซมิคอนดักเตอร์ ประกอบด้วย 27 ตารางหลัก ครอบคลุมการจัดการพนักงาน การฝึกอบรม สารเคมี อุปกรณ์ และการตอบสนองฉุกเฉิน

---

## 1. Master Tables (ตารางหลัก)

### 1.1 departments
ตารางเก็บข้อมูลแผนกต่างๆ ในองค์กร

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT | รหัสแผนก | PRIMARY KEY |
| name | VARCHAR(100) | ชื่อแผนก | NOT NULL |
| manager_id | INT | รหัสผู้จัดการแผนก | - |

**ตัวอย่างข้อมูล:**
- 1: Production (ฝ่ายผลิต)
- 2: Maintenance (ฝ่ายซ่อมบำรุง)
- 3: Quality Control (ฝ่ายควบคุมคุณภาพ)
- 4: EHS (Environment, Health & Safety)
- 5: Engineering (ฝ่ายวิศวกรรม)
- 6: Chemical Management (ฝ่ายจัดการสารเคมี)

### 1.2 areas
ตารางเก็บข้อมูลพื้นที่ต่างๆ ในโรงงาน

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT | รหัสพื้นที่ | PRIMARY KEY |
| area_code | VARCHAR(50) | รหัสย่อพื้นที่ | UNIQUE, NOT NULL |
| area_name | VARCHAR(100) | ชื่อพื้นที่ | - |
| clean_room_class | VARCHAR(20) | ระดับห้องคลีนรูม | NULL allowed |
| max_occupancy | INT | จำนวนคนสูงสุดที่อนุญาต | - |

**ตัวอย่างข้อมูล:**
- FAB-A: Fabrication Area A (Class 10000, max 50 คน)
- FAB-B: Fabrication Area B (Class 1000, max 30 คน)
- CHEM-ROOM: Chemical Storage Room (ไม่ใช่คลีนรูม, max 10 คน)
- CVD-AREA: Chemical Vapor Deposition (Class 100, max 20 คน)
- ETCH-AREA: Etching Area (Class 1000, max 25 คน)

### 1.3 employees
ตารางข้อมูลพนักงานทั้งหมด

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT | รหัสพนักงาน (ระบบ) | PRIMARY KEY |
| employee_id | VARCHAR(20) | รหัสพนักงาน (บริษัท) | UNIQUE, NOT NULL |
| name | VARCHAR(100) | ชื่อ-นามสกุล | NOT NULL |
| department_id | INT | รหัสแผนก | FOREIGN KEY → departments(id) |
| position | VARCHAR(100) | ตำแหน่งงาน | - |
| shift | CHAR(1) | กะการทำงาน (A/B/C) | - |
| hire_date | DATE | วันที่เริ่มงาน | - |
| status | VARCHAR(20) | สถานะการทำงาน | DEFAULT 'ACTIVE' |
| email | VARCHAR(100) | อีเมล | - |
| phone | VARCHAR(20) | เบอร์โทรศัพท์ | - |

**ตัวอย่างข้อมูล:**
- E1001: Somchai Jaidee (Production Operator, Shift A)
- E1004: Siriporn Thongchai (Safety Officer, Shift A)
- E1011: Apichart Somkid (Production Operator, Shift B)

---

## 2. Training & Certification (การฝึกอบรมและใบรับรอง)

### 2.1 training_records
บันทึกประวัติการฝึกอบรมของพนักงาน

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสบันทึก | PRIMARY KEY |
| employee_id | INT | รหัสพนักงาน | FOREIGN KEY → employees(id) |
| course_code | VARCHAR(50) | รหัสหลักสูตร | - |
| course_name | VARCHAR(200) | ชื่อหลักสูตร | - |
| training_date | DATE | วันที่ฝึกอบรม | - |
| expiry_date | DATE | วันหมดอายุ | - |
| score | DECIMAL(5,2) | คะแนนสอบ | - |
| status | VARCHAR(20) | สถานะ (PASSED/FAILED/EXPIRED) | - |
| trainer_name | VARCHAR(100) | ชื่อผู้ฝึกอบรม | - |
| certificate_number | VARCHAR(50) | เลขที่ใบรับรอง | - |

**หลักสูตรสำคัญ:**
- CHEM-HF-001: HF Safety Handling (16 ชั่วโมง)
- LOTO-BASIC: Lockout/Tagout Basic (8 ชั่วโมง)
- LOTO-ADV: Lockout/Tagout Advanced (8 ชั่วโมง)
- ISO-14644: Cleanroom Protocol ISO 14644 (8 ชั่วโมง)

---

## 3. PPE Management (การจัดการอุปกรณ์ป้องกันส่วนบุคคล)

### 3.1 ppe_distribution
บันทึกการเบิกจ่ายอุปกรณ์ PPE

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการเบิกจ่าย | PRIMARY KEY |
| employee_id | INT | รหัสพนักงาน | FOREIGN KEY → employees(id) |
| ppe_type | VARCHAR(100) | ประเภท PPE | - |
| ppe_model | VARCHAR(100) | รุ่น/ยี่ห้อ | - |
| size | VARCHAR(20) | ขนาด | - |
| issue_date | DATE | วันที่เบิก | - |
| expiry_date | DATE | วันหมดอายุ | - |
| condition_status | VARCHAR(20) | สภาพ (GOOD/WORN/DAMAGED) | - |
| quantity | INT | จำนวน | DEFAULT 1 |
| return_date | DATE | วันที่คืน | NULL allowed |

**ประเภท PPE หลัก:**
- Chemical Glove (Nitrile 0.12mm, 0.15mm)
- Cleanroom Suit (DuPont Tyvek)
- ESD Shoes (SafeStep ESD-200)
- Full Face Respirator (3M 6800)
- Chemical Suit Level A (DuPont Tychem)

---

## 4. Chemical Management (การจัดการสารเคมี)

### 4.1 chemical_master
ข้อมูลหลักของสารเคมีทั้งหมด

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT | รหัสสารเคมี | PRIMARY KEY |
| chemical_name | VARCHAR(100) | ชื่อสารเคมี | NOT NULL |
| cas_number | VARCHAR(50) | หมายเลข CAS | - |
| hazard_class | VARCHAR(50) | ระดับอันตราย | - |
| unit | VARCHAR(20) | หน่วยนับ | - |
| unit_cost | DECIMAL(10,2) | ราคาต่อหน่วย (บาท) | - |
| msds_url | VARCHAR(500) | ลิงก์ MSDS | - |
| storage_temp_min | DECIMAL(5,2) | อุณหภูมิเก็บต่ำสุด (°C) | - |
| storage_temp_max | DECIMAL(5,2) | อุณหภูมิเก็บสูงสุด (°C) | - |
| shelf_life_days | INT | อายุการเก็บ (วัน) | - |

**ระดับอันตราย:**
- Class I - Extremely Hazardous: HF, Phosphine, Arsine
- Class II - Highly Hazardous: H₂SO₄, Silane, Ammonia
- Class III - Moderately Hazardous: IPA, Acetone, Photoresist

### 4.2 chemical_inventory
สต็อกสารเคมีปัจจุบัน

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสสต็อก | PRIMARY KEY |
| chemical_id | INT | รหัสสารเคมี | FOREIGN KEY → chemical_master(id) |
| location | VARCHAR(100) | ตำแหน่งเก็บ | - |
| lot_number | VARCHAR(50) | เลข Lot | - |
| quantity | DECIMAL(10,3) | ปริมาณคงเหลือ | - |
| unit | VARCHAR(20) | หน่วย | - |
| received_date | DATE | วันที่รับเข้า | - |
| expiry_date | DATE | วันหมดอายุ | - |
| supplier | VARCHAR(100) | ผู้จำหน่าย | - |
| status | VARCHAR(20) | สถานะ | DEFAULT 'ACTIVE' |

### 4.3 chemical_transactions
บันทึกการเบิก-จ่ายสารเคมี

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสรายการ | PRIMARY KEY |
| chemical_id | INT | รหัสสารเคมี | FOREIGN KEY → chemical_master(id) |
| transaction_type | VARCHAR(20) | ประเภท (IN/OUT/WASTE/EXPIRED) | - |
| quantity | DECIMAL(10,3) | ปริมาณ | - |
| unit | VARCHAR(20) | หน่วย | - |
| transaction_date | DATETIME | วันเวลาทำรายการ | DEFAULT GETDATE() |
| performed_by | INT | ผู้ทำรายการ | FOREIGN KEY → employees(id) |
| purpose | VARCHAR(200) | วัตถุประสงค์ | - |
| work_order | VARCHAR(50) | เลขที่ใบสั่งงาน | - |
| from_location | VARCHAR(100) | จากที่ | - |
| to_location | VARCHAR(100) | ไปที่ | - |

### 4.4 chemical_spills
บันทึกเหตุสารเคมีหกรั่วไหล

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสเหตุการณ์ | PRIMARY KEY |
| spill_date | DATETIME | วันเวลาที่เกิดเหตุ | DEFAULT GETDATE() |
| chemical_name | VARCHAR(100) | ชื่อสารเคมี | - |
| quantity_spilled | DECIMAL(10,3) | ปริมาณที่หก | - |
| unit | VARCHAR(20) | หน่วย | - |
| area_id | INT | พื้นที่เกิดเหตุ | FOREIGN KEY → areas(id) |
| reported_by | INT | ผู้รายงาน | FOREIGN KEY → employees(id) |
| cleanup_duration_min | INT | เวลาทำความสะอาด (นาที) | - |
| severity_level | INT | ระดับความรุนแรง (1-5) | - |
| root_cause | VARCHAR(500) | สาเหตุ | - |
| corrective_action | VARCHAR(500) | การแก้ไข | - |

---

## 5. Lockout/Tagout (LOTO)

### 5.1 loto_registry
ทะเบียนการล็อกเครื่องจักร

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการล็อก | PRIMARY KEY |
| lock_number | VARCHAR(50) | หมายเลขกุญแจ | UNIQUE |
| equipment_id | VARCHAR(100) | รหัสเครื่องจักร | - |
| equipment_name | VARCHAR(200) | ชื่อเครื่องจักร | - |
| locked_by | INT | ผู้ล็อก | FOREIGN KEY → employees(id) |
| lock_time | DATETIME | เวลาล็อก | DEFAULT GETDATE() |
| unlock_time | DATETIME | เวลาปลดล็อก | NULL allowed |
| reason | VARCHAR(500) | เหตุผล | - |
| work_permit_number | VARCHAR(50) | เลขที่ใบอนุญาต | - |
| status | VARCHAR(20) | สถานะ (LOCKED/UNLOCKED) | DEFAULT 'LOCKED' |
| verified_by | INT | ผู้ตรวจสอบ | FOREIGN KEY → employees(id) |

**กฎสำคัญ:**
- ห้ามล็อกเกิน 12 ชั่วโมงโดยไม่ส่งมอบ
- ต้องมี work permit ทุกครั้ง
- ต้องถอดโดยเจ้าของกุญแจเท่านั้น

### 5.2 loto_violations
บันทึกการฝ่าฝืนระเบียบ LOTO

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการฝ่าฝืน | PRIMARY KEY |
| violation_date | DATETIME | วันเวลาที่ฝ่าฝืน | DEFAULT GETDATE() |
| equipment_id | VARCHAR(100) | รหัสเครื่องจักร | - |
| violated_by | INT | ผู้ฝ่าฝืน | FOREIGN KEY → employees(id) |
| violation_type | VARCHAR(100) | ประเภทการฝ่าฝืน | - |
| severity_level | INT | ระดับความรุนแรง (1-5) | - |
| description | VARCHAR(500) | รายละเอียด | - |
| corrective_action | VARCHAR(500) | การแก้ไข | - |
| investigated_by | INT | ผู้สอบสวน | FOREIGN KEY → employees(id) |

---

## 6. Equipment & Calibration (อุปกรณ์และการสอบเทียบ)

### 6.1 equipment_calibration
บันทึกการสอบเทียบอุปกรณ์

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการสอบเทียบ | PRIMARY KEY |
| equipment_id | VARCHAR(100) | รหัสอุปกรณ์ | - |
| equipment_type | VARCHAR(100) | ประเภทอุปกรณ์ | - |
| equipment_name | VARCHAR(200) | ชื่ออุปกรณ์ | - |
| calibration_date | DATE | วันที่สอบเทียบ | - |
| next_calibration | DATE | วันสอบเทียบครั้งถัดไป | - |
| calibrated_by | VARCHAR(100) | ผู้สอบเทียบ | - |
| certificate_number | VARCHAR(50) | เลขที่ใบรับรอง | - |
| status | VARCHAR(20) | สถานะ (VALID/OVERDUE) | - |
| location | VARCHAR(100) | ตำแหน่งติดตั้ง | - |

**อุปกรณ์สำคัญ:**
- Particle Counter (ต้องสอบเทียบทุก 3 เดือน)
- Gas Detector (ต้องสอบเทียบทุก 3 เดือน)
- Scrubber (ต้องตรวจสอบประสิทธิภาพทุกวัน)

### 6.2 equipment_incidents
บันทึกเหตุขัดข้องของอุปกรณ์

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสเหตุการณ์ | PRIMARY KEY |
| incident_date | DATETIME | วันเวลาเกิดเหตุ | DEFAULT GETDATE() |
| equipment_type | VARCHAR(100) | ประเภทอุปกรณ์ | - |
| equipment_id | VARCHAR(100) | รหัสอุปกรณ์ | - |
| incident_type | VARCHAR(100) | ประเภทเหตุการณ์ | - |
| description | VARCHAR(1000) | รายละเอียด | - |
| production_impact_hrs | DECIMAL(10,2) | ผลกระทบต่อการผลิต (ชั่วโมง) | - |
| repair_cost | DECIMAL(12,2) | ค่าซ่อม (บาท) | - |
| root_cause | VARCHAR(500) | สาเหตุ | - |
| area_id | INT | พื้นที่ | FOREIGN KEY → areas(id) |

---

## 7. Cleanroom & Particle Monitoring

### 7.1 particle_excursions
บันทึกการเกินค่ามาตรฐานของอนุภาค

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสเหตุการณ์ | PRIMARY KEY |
| excursion_date | DATETIME | วันเวลาที่เกิด | DEFAULT GETDATE() |
| area_id | INT | พื้นที่ | FOREIGN KEY → areas(id) |
| particle_count_05um | INT | จำนวนอนุภาค 0.5 μm | - |
| particle_count_5um | INT | จำนวนอนุภาค 5 μm | - |
| limit_05um | INT | ค่าจำกัด 0.5 μm | - |
| limit_5um | INT | ค่าจำกัด 5 μm | - |
| duration_minutes | INT | ระยะเวลา (นาที) | - |
| root_cause | VARCHAR(500) | สาเหตุ | - |
| corrective_action | VARCHAR(500) | การแก้ไข | - |
| production_impact | VARCHAR(200) | ผลกระทบ | - |

**มาตรฐาน ISO 14644:**
- Class 100: ≤100 particles/ft³ @ 0.5μm
- Class 1000: ≤1,000 particles/ft³ @ 0.5μm  
- Class 10000: ≤10,000 particles/ft³ @ 0.5μm

---

## 8. Gas Detection & Scrubber

### 8.1 scrubber_monitoring
ตรวจสอบประสิทธิภาพ scrubber

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการตรวจสอบ | PRIMARY KEY |
| scrubber_id | VARCHAR(50) | รหัส scrubber | - |
| reading_time | DATETIME | เวลาที่อ่านค่า | DEFAULT GETDATE() |
| efficiency_rate | DECIMAL(5,2) | ประสิทธิภาพ (%) | - |
| inlet_concentration | DECIMAL(10,3) | ความเข้มข้นขาเข้า | - |
| outlet_concentration | DECIMAL(10,3) | ความเข้มข้นขาออก | - |
| flow_rate | DECIMAL(10,2) | อัตราการไหล | - |
| ph_level | DECIMAL(4,2) | ค่า pH | - |
| temperature | DECIMAL(5,2) | อุณหภูมิ (°C) | - |
| status | VARCHAR(20) | สถานะ | - |

**เกณฑ์เตือน:**
- efficiency < 90%: WARNING
- efficiency < 85%: CRITICAL - หยุดการผลิต

### 8.2 gas_sensors
เซ็นเซอร์ตรวจจับแก๊ส

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการอ่านค่า | PRIMARY KEY |
| sensor_id | VARCHAR(50) | รหัสเซ็นเซอร์ | - |
| location | VARCHAR(100) | ตำแหน่ง | - |
| gas_type | VARCHAR(50) | ประเภทแก๊ส | - |
| reading_value | DECIMAL(10,3) | ค่าที่อ่านได้ | - |
| unit | VARCHAR(20) | หน่วย (ppm) | - |
| reading_time | DATETIME | เวลาอ่านค่า | DEFAULT GETDATE() |
| alarm_level | VARCHAR(20) | ระดับเตือน (NORMAL/WARNING/CRITICAL) | - |
| lower_limit | DECIMAL(10,3) | ขีดจำกัดล่าง | - |
| upper_limit | DECIMAL(10,3) | ขีดจำกัดบน | - |

**ค่าจำกัดแก๊สอันตราย (ppm):**
- HF: 3.0 ppm
- NH₃: 25.0 ppm
- SiH₄: 5.0 ppm
- PH₃: 0.3 ppm

### 8.3 alarm_history
ประวัติการแจ้งเตือน

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการแจ้งเตือน | PRIMARY KEY |
| alarm_time | DATETIME | เวลาแจ้งเตือน | DEFAULT GETDATE() |
| alarm_type | VARCHAR(100) | ประเภทการเตือน | - |
| sensor_id | VARCHAR(50) | รหัสเซ็นเซอร์ | - |
| area_id | INT | พื้นที่ | FOREIGN KEY → areas(id) |
| severity_level | INT | ระดับความรุนแรง (1-5) | - |
| acknowledged_by | INT | ผู้รับทราบ | FOREIGN KEY → employees(id) |
| acknowledged_time | DATETIME | เวลารับทราบ | - |
| resolution_time | DATETIME | เวลาแก้ไข | - |
| false_alarm | BIT | เป็นสัญญาณเท็จ | DEFAULT 0 |

---

## 9. Emergency Response (การตอบสนองฉุกเฉิน)

### 9.1 drill_log
บันทึกการซ้อมหนีไฟ

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสการซ้อม | PRIMARY KEY |
| drill_id | VARCHAR(50) | รหัสการซ้อม | UNIQUE |
| drill_type | VARCHAR(50) | ประเภท (FIRE/CHEMICAL/GAS) | - |
| drill_date | DATE | วันที่ซ้อม | - |
| alarm_time | DATETIME | เวลาสัญญาณเตือน | - |
| all_clear_time | DATETIME | เวลาปลอดภัย | - |
| total_evacuated | INT | จำนวนคนอพยพ | - |
| missing_persons | INT | จำนวนคนหาย | - |
| observations | VARCHAR(1000) | ข้อสังเกต | - |
| conducted_by | INT | ผู้ควบคุมการซ้อม | FOREIGN KEY → employees(id) |

**มาตรฐาน:**
- ต้องอพยพให้เสร็จภายใน 5 นาที
- ซ้อมหนีไฟเดือนละครั้ง
- ซ้อมรับมือสารเคมีทุก 6 เดือน

### 9.2 evacuation_log
บันทึกการอพยพรายบุคคล

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสบันทึก | PRIMARY KEY |
| drill_id | VARCHAR(50) | รหัสการซ้อม | FOREIGN KEY → drill_log(drill_id) |
| employee_id | INT | รหัสพนักงาน | FOREIGN KEY → employees(id) |
| area_id | INT | พื้นที่ | FOREIGN KEY → areas(id) |
| badge_out_time | DATETIME | เวลาออกจากพื้นที่ | - |
| muster_point | VARCHAR(50) | จุดรวมพล | - |
| badge_in_time | DATETIME | เวลากลับเข้า | - |

---

## 10. Safety Metrics & Incidents

### 10.1 incident_log
บันทึกอุบัติเหตุและเหตุการณ์

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสเหตุการณ์ | PRIMARY KEY |
| incident_date | DATETIME | วันเวลาเกิดเหตุ | DEFAULT GETDATE() |
| incident_type | VARCHAR(100) | ประเภทเหตุการณ์ | - |
| area_id | INT | พื้นที่เกิดเหตุ | FOREIGN KEY → areas(id) |
| severity_level | INT | ระดับความรุนแรง (1-5) | - |
| description | VARCHAR(1000) | รายละเอียด | - |
| involved_employee | INT | พนักงานที่เกี่ยวข้อง | FOREIGN KEY → employees(id) |
| injury_type | VARCHAR(200) | ประเภทการบาดเจ็บ | - |
| lost_time_days | INT | จำนวนวันหยุดงาน | DEFAULT 0 |
| medical_treatment | BIT | ต้องรักษาพยาบาล | DEFAULT 0 |
| root_cause | VARCHAR(500) | สาเหตุ | - |
| corrective_action | VARCHAR(500) | การแก้ไข | - |
| investigation_status | VARCHAR(50) | สถานะการสอบสวน | - |
| reported_to_authorities | BIT | รายงานหน่วยงานราชการ | DEFAULT 0 |

**ระดับความรุนแรง:**
- Level 1: Near miss
- Level 2: First aid only
- Level 3: Medical treatment
- Level 4: Lost time injury
- Level 5: Fatality

### 10.2 safety_metrics
ตัวชี้วัดความปลอดภัยรายเดือน

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสบันทึก | PRIMARY KEY |
| date | DATE | วันที่ (วันแรกของเดือน) | - |
| monthly_score | DECIMAL(5,2) | คะแนนความปลอดภัย (0-100) | - |
| incident_rate | DECIMAL(10,4) | อัตราอุบัติเหตุต่อล้านชั่วโมง | - |
| near_miss_count | INT | จำนวน near miss | - |
| training_compliance_rate | DECIMAL(5,2) | % การฝึกอบรมตามแผน | - |
| ppe_compliance_rate | DECIMAL(5,2) | % การใช้ PPE ถูกต้อง | - |
| audit_score | DECIMAL(5,2) | คะแนน audit (0-100) | - |
| observations | VARCHAR(500) | ข้อสังเกต | - |

---

## 11. Waste Management (การจัดการของเสีย)

### 11.1 waste_registry
ทะเบียนของเสียอันตราย

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสของเสีย | PRIMARY KEY |
| waste_id | VARCHAR(50) | รหัสของเสีย | UNIQUE |
| chemical_name | VARCHAR(100) | ชื่อสารเคมี | - |
| waste_type | VARCHAR(50) | ประเภทของเสีย | - |
| quantity | DECIMAL(10,3) | ปริมาณ | - |
| unit | VARCHAR(20) | หน่วย | - |
| generated_date | DATE | วันที่เกิด | - |
| generated_by | INT | ผู้ก่อกำเนิด | FOREIGN KEY → employees(id) |
| storage_location | VARCHAR(100) | สถานที่เก็บ | - |
| disposal_date | DATE | วันที่กำจัด | NULL allowed |
| disposal_vendor | VARCHAR(100) | บริษัทกำจัด | - |
| manifest_number | VARCHAR(50) | เลขที่ใบกำกับ | - |
| disposal_cost | DECIMAL(10,2) | ค่ากำจัด (บาท) | - |

**กฎหมาย:**
- ห้ามเก็บของเสียเกิน 30 วัน
- ต้องมี manifest ทุกครั้ง
- ต้องใช้บริษัทที่ได้รับอนุญาต

---

## 12. Regulatory Compliance (การปฏิบัติตามกฎหมาย)

### 12.1 regulatory_compliance
การติดตามการปฏิบัติตามกฎหมาย

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสข้อกำหนด | PRIMARY KEY |
| requirement | VARCHAR(500) | ข้อกำหนด | - |
| regulation | VARCHAR(100) | กฎหมาย/หน่วยงาน | - |
| department_id | INT | แผนกที่รับผิดชอบ | FOREIGN KEY → departments(id) |
| current_status | VARCHAR(20) | สถานะ (COMPLIANT/PENDING/AT RISK) | - |
| last_audit_date | DATE | วันตรวจสอบล่าสุด | - |
| next_audit_date | DATE | วันตรวจสอบครั้งถัดไป | - |
| deadline | DATE | กำหนดส่ง | - |
| penalty_amount | DECIMAL(12,2) | ค่าปรับ (บาท) | - |
| responsible_person | INT | ผู้รับผิดชอบ | FOREIGN KEY → employees(id) |
| evidence_location | VARCHAR(500) | ที่เก็บหลักฐาน | - |
| notes | VARCHAR(1000) | หมายเหตุ | - |

**หน่วยงานกำกับดูแล:**
- กรมโรงงานอุตสาหกรรม
- กรมควบคุมมลพิษ
- กรมสวัสดิการและคุ้มครองแรงงาน
- OSHA (Occupational Safety and Health Administration)
- EPA (Environmental Protection Agency)

---

## 13. Access Control (การควบคุมการเข้าถึง)

### 13.1 access_control
สิทธิการเข้าพื้นที่

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสสิทธิ | PRIMARY KEY |
| employee_id | INT | รหัสพนักงาน | FOREIGN KEY → employees(id) |
| area_code | VARCHAR(50) | รหัสพื้นที่ | - |
| access_level | VARCHAR(20) | ระดับการเข้าถึง (BASIC/FULL/MAINTENANCE/SAFETY) | - |
| valid_from | DATE | วันเริ่มต้น | - |
| valid_until | DATE | วันสิ้นสุด | - |
| training_completed | BIT | ผ่านการฝึกอบรม | DEFAULT 0 |
| ppe_issued | BIT | ได้รับ PPE | DEFAULT 0 |
| medical_clearance | BIT | ผ่านการตรวจสุขภาพ | DEFAULT 0 |
| badge_number | VARCHAR(50) | หมายเลขบัตร | - |
| created_date | DATETIME | วันที่สร้าง | DEFAULT GETDATE() |

**เงื่อนไขการเข้าพื้นที่:**
- ต้องผ่านการฝึกอบรมที่เกี่ยวข้อง
- ต้องมี PPE ที่เหมาะสม
- ต้องผ่านการตรวจสุขภาพ

---

## 14. Medical & Health (การแพทย์และสุขภาพ)

### 14.1 medical_records
บันทึกสุขภาพพนักงาน

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสบันทึก | PRIMARY KEY |
| employee_id | INT | รหัสพนักงาน | FOREIGN KEY → employees(id) |
| medical_type | VARCHAR(100) | ประเภทการตรวจ | - |
| exam_date | DATE | วันที่ตรวจ | - |
| result | VARCHAR(50) | ผลการตรวจ (PASS/FAIL/PASS WITH RESTRICTION) | - |
| next_due_date | DATE | วันนัดตรวจครั้งถัดไป | - |
| restrictions | VARCHAR(500) | ข้อจำกัด | - |
| doctor_name | VARCHAR(100) | แพทย์ผู้ตรวจ | - |
| clinic_name | VARCHAR(100) | สถานพยาบาล | - |

**การตรวจสุขภาพบังคับ:**
- Annual Health Check (ปีละครั้ง)
- Respiratory Fit Test (สำหรับผู้ใช้หน้ากาก)
- Hearing Test (สำหรับพื้นที่เสียงดัง)

---

## 15. Maintenance Schedule (ตารางซ่อมบำรุง)

### 15.1 maintenance_schedule
แผนซ่อมบำรุงเครื่องจักร

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสแผน | PRIMARY KEY |
| equipment_id | VARCHAR(100) | รหัสเครื่องจักร | - |
| equipment_name | VARCHAR(200) | ชื่อเครื่องจักร | - |
| planned_date | DATE | วันที่วางแผน | - |
| estimated_duration | INT | ระยะเวลา (ชั่วโมง) | - |
| maintenance_type | VARCHAR(50) | ประเภท (Preventive/Corrective/Calibration) | - |
| required_chemicals | VARCHAR(500) | สารเคมีที่ต้องใช้ | - |
| required_personnel | INT | จำนวนคนที่ต้องการ | - |
| criticality | VARCHAR(20) | ความสำคัญ (LOW/MEDIUM/HIGH/CRITICAL) | - |
| can_combine_with_others | BIT | สามารถทำพร้อมงานอื่นได้ | DEFAULT 0 |
| status | VARCHAR(20) | สถานะ | DEFAULT 'SCHEDULED' |
| actual_date | DATE | วันที่ทำจริง | - |
| actual_duration | INT | เวลาจริง (ชั่วโมง) | - |
| performed_by | INT | ผู้ปฏิบัติ | FOREIGN KEY → employees(id) |
| notes | VARCHAR(1000) | หมายเหตุ | - |

---

## 16. Customer & ESG

### 16.1 customer_audit_criteria
เกณฑ์การ audit จากลูกค้า

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสเกณฑ์ | PRIMARY KEY |
| customer | VARCHAR(100) | ชื่อลูกค้า | - |
| audit_requirement | VARCHAR(500) | ข้อกำหนด | - |
| category | VARCHAR(100) | หมวดหมู่ (Safety/Environment/Quality) | - |
| our_performance | DECIMAL(10,2) | ผลงานของเรา | - |
| benchmark | DECIMAL(10,2) | เกณฑ์มาตรฐาน | - |
| unit | VARCHAR(50) | หน่วยวัด | - |
| last_audit_date | DATE | วันตรวจสอบล่าสุด | - |
| next_audit_date | DATE | วันตรวจสอบครั้งถัดไป | - |
| status | VARCHAR(20) | สถานะ (PASS/FAIL/NEED IMPROVEMENT) | - |
| improvement_plan | VARCHAR(1000) | แผนปรับปรุง | - |

**ลูกค้าหลัก:**
- Apple: Incident Rate < 0.5/million hrs
- Intel: Training Compliance > 90%
- NVIDIA: Cleanroom Control > 95%
- TSMC: LOTO Compliance > 95%

### 16.2 esg_metrics
ตัวชี้วัด ESG (Environmental, Social, Governance)

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | INT IDENTITY | รหัสบันทึก | PRIMARY KEY |
| date | DATE | วันที่ (รายเดือน) | - |
| safety_score | DECIMAL(5,2) | คะแนนความปลอดภัย (0-100) | - |
| environmental_score | DECIMAL(5,2) | คะแนนสิ่งแวดล้อม (0-100) | - |
| governance_score | DECIMAL(5,2) | คะแนนธรรมาภิบาล (0-100) | - |
| carbon_emissions | DECIMAL(12,2) | ปริมาณคาร์บอน (ตัน) | - |
| water_usage | DECIMAL(12,2) | การใช้น้ำ (ลูกบาศก์เมตร) | - |
| waste_recycled_pct | DECIMAL(5,2) | % ของเสียที่รีไซเคิล | - |
| renewable_energy_pct | DECIMAL(5,2) | % พลังงานหมุนเวียน | - |
| diversity_index | DECIMAL(5,2) | ดัชนีความหลากหลาย | - |

---

## Database Relationships Summary

### Primary Relationships:
1. **employees** → หลายตาราง (training, PPE, incidents, etc.)
2. **chemical_master** → chemical_inventory → chemical_transactions
3. **areas** → incidents, particle_excursions, equipment_incidents
4. **drill_log** → evacuation_log

### Key Business Rules:
1. **Training Expiry:** ต้องต่ออายุก่อนหมดอายุ 30 วัน
2. **LOTO Duration:** ห้ามล็อกเกิน 12 ชั่วโมง
3. **Waste Storage:** ห้ามเก็บเกิน 30 วัน
4. **Scrubber Efficiency:** ต่ำกว่า 85% = หยุดการผลิต
5. **Evacuation Time:** ต้องไม่เกิน 5 นาที
6. **Gas Limits:** เกินค่ากำหนด = อพยพทันที

### Critical Queries for Safety:
1. Real-time gas monitoring
2. Scrubber efficiency tracking
3. Training expiration alerts
4. LOTO compliance check
5. Chemical inventory status
6. Regulatory deadline tracking
7. Customer audit readiness

---

*Document Version: 1.0*
*Last Updated: September 2024*
*Total Tables: 27*
*For: Semiconductor Fabrication Safety Management System*