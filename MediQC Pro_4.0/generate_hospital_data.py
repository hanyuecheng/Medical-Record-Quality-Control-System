#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医院电子病历数据库样本数据生成脚本
生成5个患者的基本数据及相关医生、科室等信息
"""

import mysql.connector
import random
import os
import sys
from datetime import datetime, timedelta
import hashlib
import getpass

# 获取数据库连接配置
def get_db_config():
    print("请输入MySQL数据库连接信息：")
    host = input("主机地址 (默认: localhost): ") or "localhost"
    user = input("用户名 (默认: root): ") or "root"
    password = getpass.getpass("密码: ")
    
    # 测试连接
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        conn.close()
        print("数据库连接测试成功！")
    except mysql.connector.Error as err:
        print(f"数据库连接失败: {err}")
        sys.exit(1)
    
    return {
        'host': host,
        'user': user,
        'password': password,
        'charset': 'utf8mb4'
    }

# 生成随机日期
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

# 生成随机身份证号
def generate_id_card():
    # 随机生成一个地区码（前6位）
    region_code = random.randint(110000, 659000)
    
    # 随机生成出生日期（中间8位）
    now = datetime.now()
    # 生成20-80岁之间的人
    start_date = now - timedelta(days=365*80)
    end_date = now - timedelta(days=365*20)
    birth_date = random_date(start_date, end_date)
    birth_code = birth_date.strftime("%Y%m%d")
    
    # 随机生成顺序码（后4位）
    sequence_code = random.randint(1, 999)  # 修改为3位数，确保总长度为18位
    sequence_str = f"{sequence_code:03d}"
    
    # 组合身份证号前17位
    id_card_17 = f"{region_code}{birth_code}{sequence_str}"
    
    # 确保id_card_17的长度为17位
    if len(id_card_17) != 17:
        # 如果不是17位，使用固定的地区码和顺序码
        id_card_17 = f"110101{birth_code}001"
    
    # 计算校验码
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    # 计算加权和
    weighted_sum = sum(int(id_card_17[i]) * weights[i] for i in range(17))
    
    # 计算校验码
    check_code = check_codes[weighted_sum % 11]
    
    # 返回完整的身份证号
    return f"{id_card_17}{check_code}"

# 生成随机手机号
def generate_phone():
    # 手机号前三位
    prefix = random.choice(['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                           '150', '151', '152', '153', '155', '156', '157', '158', '159',
                           '170', '171', '172', '173', '175', '176', '177', '178', '179',
                           '180', '181', '182', '183', '184', '185', '186', '187', '188', '189'])
    # 随机生成后8位
    suffix = ''.join(random.choice('0123456789') for _ in range(8))
    return f"{prefix}{suffix}"

# 生成地址
def generate_address():
    provinces = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '山东省', '河南省', '四川省', '湖北省', '湖南省']
    cities = ['市辖区', '广州市', '深圳市', '南京市', '苏州市', '杭州市', '宁波市', '济南市', '青岛市', '郑州市', '成都市', '武汉市', '长沙市']
    districts = ['海淀区', '朝阳区', '福田区', '南山区', '姑苏区', '虎丘区', '西湖区', '江干区', '历下区', '市中区', '金水区', '二七区', '武侯区', '锦江区', '洪山区', '江岸区', '岳麓区', '天心区']
    streets = ['中关村大街', '建国路', '深南大道', '人民路', '解放路', '和平路', '新华路', '长江路', '黄河路', '中山路']
    building_numbers = [f"{random.randint(1, 200)}号", f"{random.randint(1, 50)}栋", f"{random.randint(1, 30)}单元", f"{random.randint(101, 2505)}室"]
    
    address = random.choice(provinces) + random.choice(cities) + random.choice(districts) + random.choice(streets) + ''.join(random.sample(building_numbers, random.randint(1, 3)))
    return address

# 创建数据库和表结构
def create_database_schema(cursor):
    try:
        # 读取SQL文件
        with open('hospital_emr_schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 按语句分割SQL脚本
        sql_statements = sql_script.split(';')
        
        # 执行每条SQL语句
        for statement in sql_statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as err:
                    # 忽略一些常见的错误
                    if err.errno == 1007:  # ER_DB_CREATE_EXISTS - 数据库已存在
                        print("数据库已存在，继续执行...")
                    elif err.errno == 1050:  # ER_TABLE_EXISTS_ERROR - 表已存在
                        print(f"表已存在，继续执行...")
                    elif err.errno == 1061:  # ER_DUP_KEYNAME - 索引已存在
                        print(f"索引已存在，继续执行...")
                    elif err.errno == 1068:  # ER_MULTIPLE_PRI_KEY - 多个主键
                        print(f"主键已存在，继续执行...")
                    else:
                        print(f"执行SQL语句时出错: {err}")
                        print(f"问题语句: {statement}")
                        raise
        
        print("数据库和表结构创建成功！")
    except Exception as e:
        print(f"创建数据库和表结构时出错: {e}")
        raise

# 插入科室数据
def insert_departments(cursor):
    departments = [
        ('内科', '住院部1楼', '0101-1234567', '王主任'),
        ('外科', '住院部2楼', '0101-1234568', '李主任'),
        ('妇产科', '住院部3楼', '0101-1234569', '张主任'),
        ('儿科', '门诊部1楼', '0101-1234570', '刘主任'),
        ('神经科', '住院部4楼', '0101-1234571', '陈主任'),
        ('骨科', '住院部2楼', '0101-1234572', '杨主任'),
        ('肿瘤科', '住院部5楼', '0101-1234573', '赵主任'),
        ('眼科', '门诊部2楼', '0101-1234574', '黄主任'),
        ('耳鼻喉科', '门诊部2楼', '0101-1234575', '周主任'),
        ('口腔科', '门诊部3楼', '0101-1234576', '吴主任')
    ]
    
    dept_ids = {}
    for dept in departments:
        try:
            query = """
            INSERT INTO departments (dept_name, dept_location, dept_tel, dept_director)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, dept)
            dept_ids[dept[0]] = cursor.lastrowid
        except mysql.connector.Error as err:
            # 如果插入失败，尝试查询已存在的记录
            if err.errno == 1062:  # ER_DUP_ENTRY - 重复记录
                query = "SELECT dept_id FROM departments WHERE dept_name = %s"
                cursor.execute(query, (dept[0],))
                result = cursor.fetchone()
                if result:
                    dept_ids[dept[0]] = result[0]
                    print(f"科室 '{dept[0]}' 已存在，使用已有记录。")
            else:
                raise
    
    return dept_ids

# 插入医生数据
def insert_doctors(cursor, dept_ids):
    doctors = [
        ('王医生', '男', '主任医师', '内科', '心血管疾病', '13800000001', 'wang@hospital.com', 'MD12345'),
        ('李医生', '男', '副主任医师', '外科', '普外科手术', '13800000002', 'li@hospital.com', 'MD12346'),
        ('张医生', '女', '主任医师', '妇产科', '妇科肿瘤', '13800000003', 'zhang@hospital.com', 'MD12347'),
        ('刘医生', '女', '副主任医师', '儿科', '儿童呼吸系统疾病', '13800000004', 'liu@hospital.com', 'MD12348'),
        ('陈医生', '男', '主任医师', '神经科', '脑血管疾病', '13800000005', 'chen@hospital.com', 'MD12349'),
        ('杨医生', '男', '副主任医师', '骨科', '脊柱外科', '13800000006', 'yang@hospital.com', 'MD12350'),
        ('赵医生', '女', '主任医师', '肿瘤科', '肺癌治疗', '13800000007', 'zhao@hospital.com', 'MD12351'),
        ('黄医生', '男', '副主任医师', '眼科', '白内障手术', '13800000008', 'huang@hospital.com', 'MD12352'),
        ('周医生', '女', '主任医师', '耳鼻喉科', '鼻窦炎治疗', '13800000009', 'zhou@hospital.com', 'MD12353'),
        ('吴医生', '男', '副主任医师', '口腔科', '牙周病治疗', '13800000010', 'wu@hospital.com', 'MD12354')
    ]
    
    doctor_ids = {}
    for doctor in doctors:
        try:
            query = """
            INSERT INTO doctors (doctor_name, gender, title, dept_id, specialty, phone, email, license_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            dept_id = dept_ids[doctor[3]]
            values = (doctor[0], doctor[1], doctor[2], dept_id, doctor[4], doctor[5], doctor[6], doctor[7])
            cursor.execute(query, values)
            doctor_ids[doctor[0]] = cursor.lastrowid
        except mysql.connector.Error as err:
            # 如果插入失败，尝试查询已存在的记录
            if err.errno == 1062:  # ER_DUP_ENTRY - 重复记录
                query = "SELECT doctor_id FROM doctors WHERE doctor_name = %s"
                cursor.execute(query, (doctor[0],))
                result = cursor.fetchone()
                if result:
                    doctor_ids[doctor[0]] = result[0]
                    print(f"医生 '{doctor[0]}' 已存在，使用已有记录。")
            else:
                raise
    
    return doctor_ids

# 插入护士数据
def insert_nurses(cursor, dept_ids):
    nurses = [
        ('王护士', '女', '主管护师', '内科', '13900000001', 'RN12345'),
        ('李护士', '女', '护师', '外科', '13900000002', 'RN12346'),
        ('张护士', '女', '主管护师', '妇产科', '13900000003', 'RN12347'),
        ('刘护士', '女', '护师', '儿科', '13900000004', 'RN12348'),
        ('陈护士', '男', '护师', '神经科', '13900000005', 'RN12349')
    ]
    
    nurse_ids = {}
    for nurse in nurses:
        try:
            query = """
            INSERT INTO nurses (nurse_name, gender, title, dept_id, phone, license_number)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            dept_id = dept_ids[nurse[3]]
            values = (nurse[0], nurse[1], nurse[2], dept_id, nurse[4], nurse[5])
            cursor.execute(query, values)
            nurse_ids[nurse[0]] = cursor.lastrowid
        except mysql.connector.Error as err:
            # 如果插入失败，尝试查询已存在的记录
            if err.errno == 1062:  # ER_DUP_ENTRY - 重复记录
                query = "SELECT nurse_id FROM nurses WHERE nurse_name = %s"
                cursor.execute(query, (nurse[0],))
                result = cursor.fetchone()
                if result:
                    nurse_ids[nurse[0]] = result[0]
                    print(f"护士 '{nurse[0]}' 已存在，使用已有记录。")
            else:
                raise
    
    return nurse_ids

# 插入患者数据
def insert_patients(cursor):
    patients = [
        ('张三', '男'),
        ('李四', '男'),
        ('王五', '女'),
        ('赵六', '女'),
        ('钱七', '男')
    ]
    
    patient_ids = {}
    for patient in patients:
        try:
            # 生成随机出生日期 (20-80岁)
            now = datetime.now()
            start_date = now - timedelta(days=365*80)
            end_date = now - timedelta(days=365*20)
            birth_date = random_date(start_date, end_date)
            
            id_card = generate_id_card()
            phone = generate_phone()
            address = generate_address()
            emergency_contact = '家属' + str(random.randint(1, 5))
            emergency_phone = generate_phone()
            blood_types = ['A', 'B', 'AB', 'O', '未知']
            blood_type = random.choice(blood_types)
            allergy_history = random.choice(['无', '青霉素过敏', '海鲜过敏', '花粉过敏', '无']) 
            
            query = """
            INSERT INTO patients (patient_name, gender, birth_date, id_card, phone, address, 
                                emergency_contact, emergency_phone, blood_type, allergy_history)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (patient[0], patient[1], birth_date, id_card, phone, address, 
                    emergency_contact, emergency_phone, blood_type, allergy_history)
            cursor.execute(query, values)
            patient_ids[patient[0]] = cursor.lastrowid
        except mysql.connector.Error as err:
            # 如果插入失败，尝试查询已存在的记录
            if err.errno == 1062:  # ER_DUP_ENTRY - 重复记录
                query = "SELECT patient_id FROM patients WHERE patient_name = %s"
                cursor.execute(query, (patient[0],))
                result = cursor.fetchone()
                if result:
                    patient_ids[patient[0]] = result[0]
                    print(f"患者 '{patient[0]}' 已存在，使用已有记录。")
            else:
                raise
    
    return patient_ids

# 插入住院记录
def insert_admissions(cursor, patient_ids, dept_ids, doctor_ids):
    # 诊断列表
    diagnoses = [
        '高血压', '糖尿病', '冠心病', '肺炎', '胃炎', '肝炎', '肾炎', 
        '骨折', '脑梗塞', '脑出血', '贫血', '白血病', '肺癌', '胃癌', 
        '结肠癌', '前列腺炎', '慢性阻塞性肺疾病', '支气管炎', '支气管哮喘',
        '子宫肌瘤', '乳腺增生', '宫颈炎', '前列腺增生', '阑尾炎'
    ]
    
    # 主诉列表
    chief_complaints = [
        '发热3天', '咳嗽5天', '头痛2天', '腹痛1天', '胸闷气短3天',
        '恶心呕吐2天', '腰痛1周', '关节疼痛2周', '头晕3天', '视力下降1个月'
    ]
    
    admission_ids = {}
    for name, patient_id in patient_ids.items():
        # 随机选择科室和医生
        dept_name = random.choice(list(dept_ids.keys()))
        dept_id = dept_ids[dept_name]
        
        # 找出该科室的医生
        doctor_names = [d_name for d_name, d_id in doctor_ids.items() if d_name.split('医生')[0] + '医生' in dept_name]
        if not doctor_names:  # 如果没有找到匹配的医生，随机选择一个
            doctor_name = random.choice(list(doctor_ids.keys()))
        else:
            doctor_name = random.choice(doctor_names)
        doctor_id = doctor_ids[doctor_name]
        
        # 生成住院号
        admission_number = f"ZY{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        # 生成入院日期（过去1年内）
        now = datetime.now()
        admission_date = random_date(now - timedelta(days=365), now - timedelta(days=10))
        
        # 生成出院日期（入院后1-30天）
        discharge_date = admission_date + timedelta(days=random.randint(1, 30))
        
        # 随机生成床位号
        bed_number = f"{random.randint(1, 6)}0{random.randint(1, 9)}"
        
        # 随机选择入院类型
        admission_type = random.choice(['急诊', '门诊', '转院', '其他'])
        
        # 随机选择入院和出院诊断
        admission_diagnosis = random.choice(diagnoses)
        discharge_diagnosis = admission_diagnosis  # 大多数情况下入院和出院诊断相同
        if random.random() < 0.2:  # 20%的概率出院诊断不同
            discharge_diagnosis = random.choice(diagnoses)
        
        # 随机选择主诉
        chief_complaint = random.choice(chief_complaints)
        
        # 生成现病史
        present_illness = f"患者{chief_complaint}，无发热，无恶心呕吐，无胸闷气短，无腹痛腹泻。"
        
        # 生成既往史
        past_histories = ['无特殊疾病史', '高血压病史5年', '糖尿病病史3年', '冠心病病史2年', '手术史：阑尾切除术']
        past_history = random.choice(past_histories)
        
        # 生成治疗方案
        treatment_plans = [
            '抗感染治疗，对症支持治疗',
            '降压治疗，控制血压',
            '降糖治疗，控制血糖',
            '手术治疗，术后抗感染治疗',
            '化疗，对症支持治疗'
        ]
        treatment_plan = random.choice(treatment_plans)
        
        # 生成出院小结
        discharge_summary = f"患者{name}，因'{chief_complaint}'入院，经治疗后症状明显好转，达到出院标准，予以出院。出院诊断：{discharge_diagnosis}。"
        
        # 随机选择状态
        status = random.choice(['在院', '出院', '转科', '出院'])  # 大多数是出院状态
        
        query = """
        INSERT INTO admissions (patient_id, admission_number, dept_id, bed_number, admission_date, 
                              discharge_date, admission_type, admission_diagnosis, discharge_diagnosis, 
                              attending_doctor_id, chief_complaint, present_illness, past_history, 
                              treatment_plan, discharge_summary, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (patient_id, admission_number, dept_id, bed_number, admission_date, 
                 discharge_date, admission_type, admission_diagnosis, discharge_diagnosis, 
                 doctor_id, chief_complaint, present_illness, past_history, 
                 treatment_plan, discharge_summary, status)
        cursor.execute(query, values)
        admission_ids[name] = (cursor.lastrowid, admission_number, admission_date, discharge_date, dept_id, doctor_id, admission_diagnosis, discharge_diagnosis)
    
    return admission_ids

# 插入病案首页
def insert_medical_records(cursor, admission_ids, doctor_ids):
    for name, admission_info in admission_ids.items():
        admission_id, admission_number, admission_date, discharge_date, dept_id, doctor_id, admission_diagnosis, discharge_diagnosis = admission_info
        
        # 计算住院天数
        hospitalization_days = (discharge_date - admission_date).days
        
        # 随机生成费用
        total_cost = round(random.uniform(5000, 50000), 2)
        medicine_cost = round(total_cost * random.uniform(0.3, 0.5), 2)
        examination_cost = round(total_cost * random.uniform(0.1, 0.3), 2)
        treatment_cost = round(total_cost * random.uniform(0.1, 0.2), 2)
        nursing_cost = round(total_cost * random.uniform(0.05, 0.1), 2)
        material_cost = round(total_cost * random.uniform(0.05, 0.1), 2)
        other_cost = round(total_cost - medicine_cost - examination_cost - treatment_cost - nursing_cost - material_cost, 2)
        
        # 随机选择支付方式
        payment_method = random.choice(['自费', '医保', '商业保险', '医保'])
        
        # 生成医保号
        insurance_number = f"YB{random.randint(100000000, 999999999)}" if payment_method == '医保' else None
        
        # 随机决定是否急诊
        is_emergency = random.choice([True, False, False, False])  # 25%的概率是急诊
        
        # 随机决定是否有手术
        has_operation = random.choice([True, False, False])  # 33%的概率有手术
        
        operation_name = None
        operation_date = None
        operation_doctor_id = None
        
        if has_operation:
            operations = [
                '阑尾切除术', '胆囊切除术', '疝气修补术', '结肠切除术', '胃切除术',
                '剖腹产', '子宫肌瘤切除术', '卵巢囊肿切除术',
                '骨折内固定术', '关节置换术',
                '脑肿瘤切除术', '脑血管搭桥术'
            ]
            operation_name = random.choice(operations)
            operation_date = random_date(admission_date, discharge_date)
            
            # 随机选择手术医生
            operation_doctor_id = random.choice(list(doctor_ids.values()))
        
        query = """
        INSERT INTO medical_records (admission_id, patient_id, admission_number, admission_date, 
                                   discharge_date, dept_id, attending_doctor_id, admission_diagnosis, 
                                   discharge_diagnosis, operation_name, operation_date, operation_doctor_id, 
                                   hospitalization_days, total_cost, medicine_cost, examination_cost, 
                                   treatment_cost, nursing_cost, material_cost, other_cost, 
                                   payment_method, insurance_number, is_emergency)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 获取患者ID
        cursor.execute("SELECT patient_id FROM admissions WHERE admission_id = %s", (admission_id,))
        patient_id = cursor.fetchone()[0]
        
        values = (admission_id, patient_id, admission_number, admission_date.date(), 
                 discharge_date.date(), dept_id, doctor_id, admission_diagnosis, 
                 discharge_diagnosis, operation_name, operation_date.date() if operation_date else None, operation_doctor_id, 
                 hospitalization_days, total_cost, medicine_cost, examination_cost, 
                 treatment_cost, nursing_cost, material_cost, other_cost, 
                 payment_method, insurance_number, is_emergency)
        
        cursor.execute(query, values)

# 插入测试错误数据
def insert_test_error_data(cursor, dept_ids, doctor_ids):
    print("插入测试错误数据...")
    
    # 测试错误数据
    error_patients = [
        # 6. 正常数据（对照组）
        {
            "patient_id": 6,
            "patient_name": "张三测试",
            "gender": "男",
            "birth_date": "1980-01-01",
            "id_card": "110101198001010011",
            "phone": "13800000001",
            "dept_name": "内科",
            "admission_date": "2023-01-01",
            "discharge_date": "2023-01-10",
            "diagnosis": "高血压",
            "doctor_name": "王医生"
        },
        # 7. 缺失性别信息
        {
            "patient_id": 7,
            "patient_name": "李四测试",
            "gender": "未知",  # 改为'未知'，因为数据库中性别字段是ENUM类型
            "birth_date": "1985-02-15",
            "id_card": "110101198502150022",
            "phone": "13800000002",
            "dept_name": "外科",
            "admission_date": "2023-02-01",
            "discharge_date": "2023-02-12",
            "diagnosis": "阑尾炎",
            "doctor_name": "李医生"
        },
        # 8. 性别与科室不匹配（男性挂妇产科）
        {
            "patient_id": 8,
            "patient_name": "王五测试",
            "gender": "男",
            "birth_date": "1990-03-20",
            "id_card": "110101199003200033",
            "phone": "13800000003",
            "dept_name": "妇产科",  # 逻辑错误：男性挂妇产科
            "admission_date": "2023-03-05",
            "discharge_date": "2023-03-15",
            "diagnosis": "盆腔炎",  # 逻辑错误：男性患妇科疾病
            "doctor_name": "张医生"
        },
        # 9. 出院日期早于入院日期
        {
            "patient_id": 9,
            "patient_name": "赵六测试",
            "gender": "女",
            "birth_date": "1975-04-25",
            "id_card": "110101197504250044",
            "phone": "13800000004",
            "dept_name": "神经科",
            "admission_date": "2023-04-10",
            "discharge_date": "2023-04-05",  # 逻辑错误：出院日期早于入院日期
            "diagnosis": "偏头痛",
            "doctor_name": "陈医生"
        },
        # 10. 多项错误：缺失诊断信息，电话号码格式错误
        {
            "patient_id": 10,
            "patient_name": "钱七测试",
            "gender": "女",
            "birth_date": "1995-05-30",
            "id_card": "110101199505300055",
            "phone": "138000",  # 错误：电话号码不完整
            "dept_name": "儿科",  # 逻辑错误：成年人挂儿科
            "admission_date": "2023-05-15",
            "discharge_date": "2023-05-25",
            "diagnosis": "",  # 缺失诊断
            "doctor_name": "刘医生"
        }
    ]
    
    patient_ids = {}
    for patient in error_patients:
        try:
            # 插入患者基本信息
            query = """
            INSERT INTO patients (patient_name, gender, birth_date, id_card, phone, address, 
                                emergency_contact, emergency_phone, blood_type, allergy_history)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 随机生成一些基本信息
            address = generate_address()
            emergency_contact = '家属' + str(random.randint(1, 5))
            emergency_phone = generate_phone()
            blood_type = random.choice(['A', 'B', 'AB', 'O', '未知'])
            allergy_history = random.choice(['无', '青霉素过敏', '海鲜过敏', '花粉过敏', '无'])
            
            values = (
                patient["patient_name"], 
                patient["gender"], 
                patient["birth_date"], 
                patient["id_card"], 
                patient["phone"], 
                address,
                emergency_contact, 
                emergency_phone, 
                blood_type, 
                allergy_history
            )
            
            cursor.execute(query, values)
            patient_id = cursor.lastrowid
            patient_ids[patient["patient_name"]] = patient_id
            
            # 插入住院记录
            # 获取科室ID和医生ID
            dept_id = dept_ids[patient["dept_name"]]
            doctor_id = doctor_ids[patient["doctor_name"]]
            
            # 生成住院号
            admission_number = f"ZY{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            # 转换日期格式
            admission_date = datetime.strptime(patient["admission_date"], "%Y-%m-%d")
            discharge_date = datetime.strptime(patient["discharge_date"], "%Y-%m-%d")
            
            # 随机生成床位号
            bed_number = f"{random.randint(1, 6)}0{random.randint(1, 9)}"
            
            # 随机选择入院类型
            admission_type = random.choice(['急诊', '门诊', '转院', '其他'])
            
            # 诊断信息
            admission_diagnosis = patient["diagnosis"]
            discharge_diagnosis = patient["diagnosis"]
            
            # 随机生成其他信息
            chief_complaint = f"患者主诉{random.choice(['头痛', '腹痛', '胸闷', '咳嗽', '发热'])}数日"
            present_illness = f"患者{chief_complaint}，无其他不适。"
            past_history = random.choice(['无特殊疾病史', '高血压病史5年', '糖尿病病史3年', '冠心病病史2年', '无'])
            treatment_plan = random.choice([
                '抗感染治疗，对症支持治疗',
                '降压治疗，控制血压',
                '降糖治疗，控制血糖',
                '手术治疗，术后抗感染治疗',
                '对症治疗'
            ])
            discharge_summary = f"患者{patient['patient_name']}，经治疗后症状好转，予以出院。"
            status = random.choice(['在院', '出院', '转科', '出院'])
            
            query = """
            INSERT INTO admissions (patient_id, admission_number, dept_id, bed_number, admission_date, 
                                  discharge_date, admission_type, admission_diagnosis, discharge_diagnosis, 
                                  attending_doctor_id, chief_complaint, present_illness, past_history, 
                                  treatment_plan, discharge_summary, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                patient_id, 
                admission_number, 
                dept_id, 
                bed_number, 
                admission_date, 
                discharge_date, 
                admission_type, 
                admission_diagnosis, 
                discharge_diagnosis, 
                doctor_id, 
                chief_complaint, 
                present_illness, 
                past_history, 
                treatment_plan, 
                discharge_summary, 
                status
            )
            
            cursor.execute(query, values)
            admission_id = cursor.lastrowid
            
            # 插入病案首页
            # 计算住院天数
            hospitalization_days = (discharge_date - admission_date).days
            if hospitalization_days < 0:  # 处理出院日期早于入院日期的情况
                hospitalization_days = abs(hospitalization_days)
            
            # 随机生成费用
            total_cost = round(random.uniform(5000, 50000), 2)
            medicine_cost = round(total_cost * random.uniform(0.3, 0.5), 2)
            examination_cost = round(total_cost * random.uniform(0.1, 0.3), 2)
            treatment_cost = round(total_cost * random.uniform(0.1, 0.2), 2)
            nursing_cost = round(total_cost * random.uniform(0.05, 0.1), 2)
            material_cost = round(total_cost * random.uniform(0.05, 0.1), 2)
            other_cost = round(total_cost - medicine_cost - examination_cost - treatment_cost - nursing_cost - material_cost, 2)
            
            # 随机选择支付方式
            payment_method = random.choice(['自费', '医保', '商业保险', '其他'])
            insurance_number = f"YB{random.randint(100000, 999999)}" if payment_method == '医保' else None
            
            # 是否急诊
            is_emergency = random.choice([True, False])
            
            query = """
            INSERT INTO medical_records (admission_id, patient_id, admission_number, admission_date, 
                                       discharge_date, dept_id, attending_doctor_id, admission_diagnosis, 
                                       discharge_diagnosis, hospitalization_days, total_cost, medicine_cost, 
                                       examination_cost, treatment_cost, nursing_cost, material_cost, 
                                       other_cost, payment_method, insurance_number, is_emergency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                admission_id, 
                patient_id, 
                admission_number, 
                admission_date, 
                discharge_date, 
                dept_id, 
                doctor_id, 
                admission_diagnosis, 
                discharge_diagnosis, 
                hospitalization_days, 
                total_cost, 
                medicine_cost, 
                examination_cost, 
                treatment_cost, 
                nursing_cost, 
                material_cost, 
                other_cost, 
                payment_method, 
                insurance_number, 
                is_emergency
            )
            
            cursor.execute(query, values)
            
        except mysql.connector.Error as err:
            print(f"插入测试数据时出错 (患者 {patient['patient_name']}): {err}")
            raise
    
    return patient_ids

# 主函数
def main():
    try:
        print("="*50)
        print("医院电子病历数据库样本数据生成脚本")
        print("="*50)
        print("\n该脚本将创建医院电子病历数据库并生成5个患者的样本数据。\n")
        
        # 获取数据库连接配置
        db_config = get_db_config()
        
        # 连接到MySQL数据库（不指定数据库名）
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        print("\n开始创建数据库和表结构...")
        create_database_schema(cursor)
        
        # 重新连接到新创建的数据库
        conn.close()
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database='hospital_emr',
            charset=db_config['charset']
        )
        cursor = conn.cursor()
        
        print("\n开始生成样本数据...")
        
        # 插入科室数据
        print("插入科室数据...")
        dept_ids = insert_departments(cursor)
        
        # 插入医生数据
        print("插入医生数据...")
        doctor_ids = insert_doctors(cursor, dept_ids)
        
        # 插入护士数据
        print("插入护士数据...")
        nurse_ids = insert_nurses(cursor, dept_ids)
        
        # 插入患者数据
        print("插入患者数据...")
        patient_ids = insert_patients(cursor)
        
        # 插入住院记录
        print("插入住院记录...")
        admission_ids = insert_admissions(cursor, patient_ids, dept_ids, doctor_ids)
        
        # 插入病案首页
        print("插入病案首页...")
        insert_medical_records(cursor, admission_ids, doctor_ids)
        
        # 插入测试错误数据
        error_patient_ids = insert_test_error_data(cursor, dept_ids, doctor_ids)
        
        # 提交事务
        conn.commit()
        print("\n样本数据生成完成！")
        
        # 显示数据库信息
        print("\n数据库信息:")
        print(f"- 数据库名称: hospital_emr")
        print(f"- 科室数量: {len(dept_ids)}")
        print(f"- 医生数量: {len(doctor_ids)}")
        print(f"- 护士数量: {len(nurse_ids)}")
        print(f"- 患者数量: {len(patient_ids) + len(error_patient_ids)}")
        print(f"- 正常患者: {len(patient_ids)}")
        print(f"- 测试患者: {len(error_patient_ids)}")
        
        # 显示测试数据信息
        print("\n测试数据包含以下错误:")
        print("1. 患者'李四测试': 缺失性别信息")
        print("2. 患者'王五测试': 男性挂妇产科且诊断为妇科疾病")
        print("3. 患者'赵六测试': 出院日期早于入院日期")
        print("4. 患者'钱七测试': 电话号码格式错误，成年人挂儿科，缺失诊断信息")
        
    except mysql.connector.Error as err:
        print(f"\n数据库错误: {err}")
        if 'conn' in locals():
            conn.rollback()
    except Exception as e:
        print(f"\n程序错误: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    main() 
    