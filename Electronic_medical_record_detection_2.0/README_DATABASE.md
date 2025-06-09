# 医院电子病历数据库使用说明

本项目包含一个完整的医院电子病历数据库设计和样本数据生成脚本，可以用于模拟三甲医院的电子病历系统。

## 文件说明

- `hospital_emr_schema.sql`: 数据库架构SQL脚本，包含所有表结构定义
- `generate_hospital_data.py`: 样本数据生成脚本，用于填充数据库

## 数据库架构

该数据库设计模拟了医院电子病历系统的核心组件，包括：

1. 科室管理（departments）
2. 医生信息（doctors）
3. 护士信息（nurses）
4. 患者基本信息（patients）
5. 住院记录（admissions）
6. 病案首页（medical_records）
7. 病程记录（progress_notes）
8. 医嘱管理（orders）
9. 护理记录（nursing_records）
10. 检验申请和结果（lab_requests, lab_results）
11. 检查申请和结果（examination_requests, examination_results）
12. 手术记录（operation_records）
13. 药品和用药记录（medications, medication_records）
14. 体征记录（vital_signs）
15. 诊断编码和患者诊断（diagnosis_codes, patient_diagnoses）

## 使用方法

### 1. 创建数据库

使用MySQL创建数据库并导入表结构：

```bash
# 登录MySQL
mysql -u 用户名 -p

# 或者使用MySQL Workbench或Navicat等工具执行以下SQL脚本
```

或者直接导入SQL文件：

```bash
mysql -u 用户名 -p < hospital_emr_schema.sql
```

### 2. 配置数据生成脚本

编辑 `generate_hospital_data.py` 文件，修改数据库连接配置：

```python
# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': '你的MySQL用户名',
    'password': '你的MySQL密码',
    'database': 'hospital_emr',
    'charset': 'utf8mb4'
}
```

### 3. 安装依赖

```bash
pip install mysql-connector-python
```

### 4. 生成样本数据

```bash
python generate_hospital_data.py
```

脚本将生成5个患者的样本数据，包括相关的医生、科室、住院记录等信息。

## 数据库使用示例

### 查询患者基本信息

```sql
SELECT * FROM patients;
```

### 查询患者住院记录

```sql
SELECT p.patient_name, a.admission_number, a.admission_date, a.discharge_date, 
       d.dept_name, doc.doctor_name
FROM admissions a
JOIN patients p ON a.patient_id = p.patient_id
JOIN departments d ON a.dept_id = d.dept_id
JOIN doctors doc ON a.attending_doctor_id = doc.doctor_id;
```

### 查询病案首页

```sql
SELECT p.patient_name, m.admission_number, m.admission_date, m.discharge_date,
       m.admission_diagnosis, m.discharge_diagnosis, m.hospitalization_days,
       m.total_cost, d.dept_name, doc.doctor_name
FROM medical_records m
JOIN patients p ON m.patient_id = p.patient_id
JOIN departments d ON m.dept_id = d.dept_id
JOIN doctors doc ON m.attending_doctor_id = doc.doctor_id;
```

## 与电子病历质控系统集成

本数据库可以与电子病历质控系统集成，步骤如下：

1. 从数据库导出病案首页数据为Excel格式：

```sql
SELECT 
    p.patient_name as '姓名',
    p.gender as '性别',
    TIMESTAMPDIFF(YEAR, p.birth_date, CURRENT_DATE()) as '年龄',
    m.admission_date as '入院日期',
    m.discharge_date as '出院日期',
    m.hospitalization_days as '住院天数',
    d.dept_name as '科室',
    doc.doctor_name as '主治医师',
    m.admission_diagnosis as '入院诊断',
    m.discharge_diagnosis as '出院诊断',
    m.operation_name as '手术名称',
    m.operation_date as '手术日期',
    m.total_cost as '总费用'
FROM medical_records m
JOIN patients p ON m.patient_id = p.patient_id
JOIN departments d ON m.dept_id = d.dept_id
JOIN doctors doc ON m.attending_doctor_id = doc.doctor_id;
```

2. 将导出的Excel文件导入到电子病历质控系统中进行检查

## 注意事项

- 本数据库仅包含模拟数据，不包含真实患者信息
- 在实际应用中，需要根据医院的具体需求调整表结构和数据生成逻辑
- 处理医疗数据时，必须严格遵守相关法律法规和医院的数据管理规定 