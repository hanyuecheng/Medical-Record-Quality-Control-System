-- 创建医院电子病历数据库
CREATE DATABASE IF NOT EXISTS hospital_emr DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hospital_emr;

-- 部门表
CREATE TABLE IF NOT EXISTS departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL COMMENT '科室名称',
    dept_location VARCHAR(100) COMMENT '科室位置',
    dept_tel VARCHAR(20) COMMENT '科室电话',
    dept_director VARCHAR(50) COMMENT '科室主任',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='医院科室信息表';

-- 医生表
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_id INT NOT NULL COMMENT '所属科室ID',
    doctor_name VARCHAR(50) NOT NULL COMMENT '医生姓名',
    gender ENUM('男', '女') NOT NULL COMMENT '性别',
    title VARCHAR(20) COMMENT '职称',
    specialty VARCHAR(100) COMMENT '专长',
    phone VARCHAR(20) COMMENT '联系电话',
    email VARCHAR(50) COMMENT '电子邮箱',
    license_number VARCHAR(30) COMMENT '医师执照号',
    status ENUM('在职', '离职', '休假') DEFAULT '在职' COMMENT '状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
) COMMENT='医生信息表';

-- 护士表
CREATE TABLE IF NOT EXISTS nurses (
    nurse_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_id INT NOT NULL COMMENT '所属科室ID',
    nurse_name VARCHAR(50) NOT NULL COMMENT '护士姓名',
    gender ENUM('男', '女') NOT NULL COMMENT '性别',
    title VARCHAR(20) COMMENT '职称',
    phone VARCHAR(20) COMMENT '联系电话',
    license_number VARCHAR(30) COMMENT '护士执照号',
    status ENUM('在职', '离职', '休假') DEFAULT '在职' COMMENT '状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
) COMMENT='护士信息表';

-- 患者基本信息表
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    gender ENUM('男', '女', '未知') NOT NULL COMMENT '性别',
    birth_date DATE COMMENT '出生日期',
    id_card VARCHAR(20) COMMENT '身份证号',
    phone VARCHAR(20) COMMENT '联系电话',
    address VARCHAR(200) COMMENT '家庭住址',
    emergency_contact VARCHAR(50) COMMENT '紧急联系人',
    emergency_phone VARCHAR(20) COMMENT '紧急联系电话',
    blood_type ENUM('A', 'B', 'AB', 'O', '未知') DEFAULT '未知' COMMENT '血型',
    allergy_history TEXT COMMENT '过敏史',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='患者基本信息表';

-- 住院记录表
CREATE TABLE IF NOT EXISTS admissions (
    admission_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL COMMENT '患者ID',
    admission_number VARCHAR(20) NOT NULL COMMENT '住院号',
    dept_id INT NOT NULL COMMENT '入院科室ID',
    bed_number VARCHAR(10) COMMENT '床位号',
    admission_date DATETIME NOT NULL COMMENT '入院日期时间',
    discharge_date DATETIME COMMENT '出院日期时间',
    admission_type ENUM('急诊', '门诊', '转院', '其他') COMMENT '入院类型',
    admission_diagnosis TEXT COMMENT '入院诊断',
    discharge_diagnosis TEXT COMMENT '出院诊断',
    attending_doctor_id INT COMMENT '主治医师ID',
    chief_complaint TEXT COMMENT '主诉',
    present_illness TEXT COMMENT '现病史',
    past_history TEXT COMMENT '既往史',
    treatment_plan TEXT COMMENT '治疗方案',
    discharge_summary TEXT COMMENT '出院小结',
    status ENUM('在院', '出院', '转科', '死亡') DEFAULT '在院' COMMENT '状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
    FOREIGN KEY (attending_doctor_id) REFERENCES doctors(doctor_id)
) COMMENT='住院记录表';

-- 病案首页表
CREATE TABLE IF NOT EXISTS medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    admission_number VARCHAR(20) NOT NULL COMMENT '住院号',
    admission_date DATE NOT NULL COMMENT '入院日期',
    discharge_date DATE COMMENT '出院日期',
    dept_id INT NOT NULL COMMENT '科室ID',
    attending_doctor_id INT NOT NULL COMMENT '主治医师ID',
    admission_diagnosis TEXT COMMENT '入院诊断',
    discharge_diagnosis TEXT COMMENT '出院诊断',
    operation_name VARCHAR(200) COMMENT '手术名称',
    operation_date DATE COMMENT '手术日期',
    operation_doctor_id INT COMMENT '手术医师ID',
    hospitalization_days INT COMMENT '住院天数',
    total_cost DECIMAL(10,2) COMMENT '总费用',
    medicine_cost DECIMAL(10,2) COMMENT '药品费用',
    examination_cost DECIMAL(10,2) COMMENT '检查费用',
    treatment_cost DECIMAL(10,2) COMMENT '治疗费用',
    nursing_cost DECIMAL(10,2) COMMENT '护理费用',
    material_cost DECIMAL(10,2) COMMENT '材料费用',
    other_cost DECIMAL(10,2) COMMENT '其他费用',
    payment_method ENUM('自费', '医保', '商业保险', '其他') COMMENT '支付方式',
    insurance_number VARCHAR(50) COMMENT '医保号',
    is_emergency BOOLEAN DEFAULT FALSE COMMENT '是否急诊',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
    FOREIGN KEY (attending_doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (operation_doctor_id) REFERENCES doctors(doctor_id)
) COMMENT='病案首页表';

-- 病程记录表
CREATE TABLE IF NOT EXISTS progress_notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    doctor_id INT NOT NULL COMMENT '记录医生ID',
    note_type ENUM('首次病程记录', '日常病程记录', '上级医师查房记录', '交接班记录', '阶段小结', '其他') COMMENT '记录类型',
    note_date DATETIME NOT NULL COMMENT '记录日期时间',
    subjective TEXT COMMENT '主观描述',
    objective TEXT COMMENT '客观检查',
    assessment TEXT COMMENT '评估',
    plan TEXT COMMENT '计划',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
) COMMENT='病程记录表';

-- 医嘱表
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    doctor_id INT NOT NULL COMMENT '开医嘱医生ID',
    order_type ENUM('长期医嘱', '临时医嘱') NOT NULL COMMENT '医嘱类型',
    order_content TEXT NOT NULL COMMENT '医嘱内容',
    start_date DATETIME NOT NULL COMMENT '开始日期时间',
    end_date DATETIME COMMENT '结束日期时间',
    frequency VARCHAR(50) COMMENT '频次',
    dosage VARCHAR(50) COMMENT '剂量',
    route VARCHAR(50) COMMENT '给药途径',
    status ENUM('待执行', '执行中', '已完成', '已取消') DEFAULT '待执行' COMMENT '状态',
    cancel_reason TEXT COMMENT '取消原因',
    cancel_doctor_id INT COMMENT '取消医生ID',
    cancel_time DATETIME COMMENT '取消时间',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (cancel_doctor_id) REFERENCES doctors(doctor_id)
) COMMENT='医嘱表';

-- 护理记录表
CREATE TABLE IF NOT EXISTS nursing_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    nurse_id INT NOT NULL COMMENT '护士ID',
    record_date DATETIME NOT NULL COMMENT '记录日期时间',
    temperature DECIMAL(3,1) COMMENT '体温',
    pulse INT COMMENT '脉搏',
    respiration INT COMMENT '呼吸',
    blood_pressure VARCHAR(20) COMMENT '血压',
    oxygen_saturation INT COMMENT '血氧饱和度',
    intake VARCHAR(100) COMMENT '入量',
    output VARCHAR(100) COMMENT '出量',
    nursing_assessment TEXT COMMENT '护理评估',
    nursing_intervention TEXT COMMENT '护理措施',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id)
) COMMENT='护理记录表';

-- 检验申请表
CREATE TABLE IF NOT EXISTS lab_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    doctor_id INT NOT NULL COMMENT '申请医生ID',
    request_date DATETIME NOT NULL COMMENT '申请日期时间',
    test_type VARCHAR(100) NOT NULL COMMENT '检验类型',
    specimen_type VARCHAR(50) COMMENT '标本类型',
    collection_time DATETIME COMMENT '采集时间',
    status ENUM('待采集', '已采集', '检验中', '已完成', '已取消') DEFAULT '待采集' COMMENT '状态',
    urgent BOOLEAN DEFAULT FALSE COMMENT '是否加急',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
) COMMENT='检验申请表';

-- 检验结果表
CREATE TABLE IF NOT EXISTS lab_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL COMMENT '检验申请ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    test_item VARCHAR(100) NOT NULL COMMENT '检验项目',
    result TEXT NOT NULL COMMENT '结果',
    reference_range VARCHAR(100) COMMENT '参考范围',
    abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
    test_date DATETIME NOT NULL COMMENT '检验日期时间',
    technician VARCHAR(50) COMMENT '检验技师',
    reviewer VARCHAR(50) COMMENT '审核人',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES lab_requests(request_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
) COMMENT='检验结果表';

-- 检查申请表
CREATE TABLE IF NOT EXISTS examination_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    doctor_id INT NOT NULL COMMENT '申请医生ID',
    request_date DATETIME NOT NULL COMMENT '申请日期时间',
    exam_type VARCHAR(100) NOT NULL COMMENT '检查类型',
    exam_part VARCHAR(100) COMMENT '检查部位',
    clinical_diagnosis TEXT COMMENT '临床诊断',
    status ENUM('待检查', '检查中', '已完成', '已取消') DEFAULT '待检查' COMMENT '状态',
    urgent BOOLEAN DEFAULT FALSE COMMENT '是否加急',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
) COMMENT='检查申请表';

-- 检查结果表
CREATE TABLE IF NOT EXISTS examination_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL COMMENT '检查申请ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    exam_date DATETIME NOT NULL COMMENT '检查日期时间',
    findings TEXT NOT NULL COMMENT '检查所见',
    impression TEXT COMMENT '印象',
    recommendation TEXT COMMENT '建议',
    image_url VARCHAR(255) COMMENT '影像URL',
    doctor_id INT COMMENT '检查医生ID',
    reviewer_id INT COMMENT '审核医生ID',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES examination_requests(request_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (reviewer_id) REFERENCES doctors(doctor_id)
) COMMENT='检查结果表';

-- 手术记录表
CREATE TABLE IF NOT EXISTS operation_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    operation_name VARCHAR(200) NOT NULL COMMENT '手术名称',
    operation_code VARCHAR(50) COMMENT '手术编码',
    operation_date DATETIME NOT NULL COMMENT '手术日期时间',
    end_time DATETIME COMMENT '结束时间',
    duration INT COMMENT '手术时长(分钟)',
    surgeon_id INT NOT NULL COMMENT '主刀医生ID',
    assistant_surgeon_ids VARCHAR(100) COMMENT '助手医生IDs',
    anesthetist_id INT COMMENT '麻醉医生ID',
    anesthesia_type VARCHAR(50) COMMENT '麻醉方式',
    operation_description TEXT COMMENT '手术描述',
    preoperative_diagnosis TEXT COMMENT '术前诊断',
    postoperative_diagnosis TEXT COMMENT '术后诊断',
    complications TEXT COMMENT '并发症',
    blood_loss INT COMMENT '失血量(ml)',
    status ENUM('已计划', '已完成', '已取消') DEFAULT '已计划' COMMENT '状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (surgeon_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (anesthetist_id) REFERENCES doctors(doctor_id)
) COMMENT='手术记录表';

-- 药品表
CREATE TABLE IF NOT EXISTS medications (
    medication_id INT AUTO_INCREMENT PRIMARY KEY,
    medication_name VARCHAR(100) NOT NULL COMMENT '药品名称',
    generic_name VARCHAR(100) COMMENT '通用名',
    medication_type ENUM('处方药', '非处方药') DEFAULT '处方药' COMMENT '药品类型',
    specification VARCHAR(50) COMMENT '规格',
    unit VARCHAR(20) COMMENT '单位',
    manufacturer VARCHAR(100) COMMENT '生产厂家',
    price DECIMAL(10,2) COMMENT '单价',
    stock INT COMMENT '库存',
    status ENUM('在用', '停用') DEFAULT '在用' COMMENT '状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='药品表';

-- 用药记录表
CREATE TABLE IF NOT EXISTS medication_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    medication_id INT NOT NULL COMMENT '药品ID',
    order_id INT COMMENT '医嘱ID',
    doctor_id INT NOT NULL COMMENT '医生ID',
    nurse_id INT COMMENT '执行护士ID',
    administration_time DATETIME COMMENT '给药时间',
    dosage VARCHAR(50) COMMENT '剂量',
    route VARCHAR(50) COMMENT '给药途径',
    frequency VARCHAR(50) COMMENT '频次',
    status ENUM('待执行', '已执行', '已取消') DEFAULT '待执行' COMMENT '状态',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id)
) COMMENT='用药记录表';

-- 体征记录表
CREATE TABLE IF NOT EXISTS vital_signs (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    nurse_id INT NOT NULL COMMENT '记录护士ID',
    record_time DATETIME NOT NULL COMMENT '记录时间',
    temperature DECIMAL(3,1) COMMENT '体温',
    pulse INT COMMENT '脉搏',
    respiration INT COMMENT '呼吸',
    systolic_pressure INT COMMENT '收缩压',
    diastolic_pressure INT COMMENT '舒张压',
    oxygen_saturation INT COMMENT '血氧饱和度',
    pain_score INT COMMENT '疼痛评分',
    consciousness VARCHAR(50) COMMENT '意识状态',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id)
) COMMENT='体征记录表';

-- 诊断编码表
CREATE TABLE IF NOT EXISTS diagnosis_codes (
    code_id INT AUTO_INCREMENT PRIMARY KEY,
    icd_code VARCHAR(20) NOT NULL COMMENT 'ICD编码',
    diagnosis_name VARCHAR(200) NOT NULL COMMENT '诊断名称',
    category VARCHAR(100) COMMENT '分类',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='诊断编码表';

-- 患者诊断表
CREATE TABLE IF NOT EXISTS patient_diagnoses (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    admission_id INT NOT NULL COMMENT '住院记录ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    doctor_id INT NOT NULL COMMENT '诊断医生ID',
    code_id INT COMMENT '诊断编码ID',
    diagnosis_type ENUM('主要诊断', '次要诊断', '并发症', '合并症') COMMENT '诊断类型',
    diagnosis_date DATE NOT NULL COMMENT '诊断日期',
    diagnosis_description TEXT NOT NULL COMMENT '诊断描述',
    is_final BOOLEAN DEFAULT FALSE COMMENT '是否最终诊断',
    notes TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (code_id) REFERENCES diagnosis_codes(code_id)
) COMMENT='患者诊断表';

-- 创建索引
CREATE INDEX idx_patients_name ON patients(patient_name);
CREATE INDEX idx_patients_idcard ON patients(id_card);
CREATE INDEX idx_admissions_number ON admissions(admission_number);
CREATE INDEX idx_admissions_dates ON admissions(admission_date, discharge_date);
CREATE INDEX idx_medical_records_dates ON medical_records(admission_date, discharge_date);
CREATE INDEX idx_orders_dates ON orders(start_date, end_date);
CREATE INDEX idx_progress_notes_date ON progress_notes(note_date);
CREATE INDEX idx_lab_requests_date ON lab_requests(request_date);
CREATE INDEX idx_examination_requests_date ON examination_requests(request_date);
CREATE INDEX idx_operation_records_date ON operation_records(operation_date);