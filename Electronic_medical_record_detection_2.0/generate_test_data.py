#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医院电子病历错误数据生成脚本
生成5个包含各种错误的测试记录，用于测试质量控制规则
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import random

# 创建输出目录
os.makedirs("sample", exist_ok=True)

# 生成随机日期
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

# 生成测试数据
def generate_test_data():
    # 创建包含错误的患者数据
    patients = [
        # 1. 正常数据（对照组）
        {
            "patient_id": 6,
            "patient_name": "张三",
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
        # 2. 缺失性别信息
        {
            "patient_id": 7,
            "patient_name": "李四",
            "gender": "",  # 缺失性别
            "birth_date": "1985-02-15",
            "id_card": "110101198502150022",
            "phone": "13800000002",
            "dept_name": "外科",
            "admission_date": "2023-02-01",
            "discharge_date": "2023-02-12",
            "diagnosis": "阑尾炎",
            "doctor_name": "李医生"
        },
        # 3. 性别与科室不匹配（男性挂妇产科）
        {
            "patient_id": 8,
            "patient_name": "王五",
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
        # 4. 出院日期早于入院日期
        {
            "patient_id": 9,
            "patient_name": "赵六",
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
        # 5. 多项错误：缺失诊断信息，电话号码格式错误
        {
            "patient_id": 10,
            "patient_name": "钱七",
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
    
    # 转换为DataFrame
    df = pd.DataFrame(patients)
    
    # 保存为Excel文件
    excel_path = os.path.join("sample", "test_data_with_errors.xlsx")
    df.to_excel(excel_path, index=False)
    
    print(f"测试数据已生成并保存至: {excel_path}")
    print("包含以下错误:")
    print("1. 患者7: 缺失性别信息")
    print("2. 患者8: 男性挂妇产科且诊断为妇科疾病")
    print("3. 患者9: 出院日期早于入院日期")
    print("4. 患者10: 电话号码格式错误，成年人挂儿科，缺失诊断信息")
    
    return df

if __name__ == "__main__":
    print("="*50)
    print("医院电子病历错误数据生成脚本")
    print("="*50)
    print("生成5个包含各种错误的测试记录，用于测试质量控制规则")
    print()
    
    # 生成测试数据
    df = generate_test_data() 