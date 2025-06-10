#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
医院电子病历数据导出脚本
将病案首页数据导出为Excel格式，以便与电子病历质控系统集成
"""

import mysql.connector
import pandas as pd
import sys
import getpass
from datetime import datetime

# 获取数据库连接配置
def get_db_config():
    print("请输入MySQL数据库连接信息：")
    host = input("主机地址 (默认: localhost): ") or "localhost"
    user = input("用户名 (默认: root): ") or "root"
    password = getpass.getpass("密码: ")
    database = input("数据库名称 (默认: hospital_emr): ") or "hospital_emr"
    
    # 测试连接
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
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
        'database': database,
        'charset': 'utf8mb4'
    }

# 导出病案首页数据
def export_medical_records(conn):
    # SQL查询语句
    query = """
    SELECT 
        p.patient_name as '姓名',
        p.gender as '性别',
        TIMESTAMPDIFF(YEAR, p.birth_date, CURRENT_DATE()) as '年龄',
        p.id_card as '身份证号',
        m.admission_number as '住院号',
        m.admission_date as '入院日期',
        m.discharge_date as '出院日期',
        m.hospitalization_days as '住院天数',
        d.dept_name as '科室',
        doc.doctor_name as '主治医师',
        m.admission_diagnosis as '入院诊断',
        m.discharge_diagnosis as '出院诊断',
        m.operation_name as '手术名称',
        m.operation_date as '手术日期',
        m.total_cost as '总费用',
        m.medicine_cost as '药品费用',
        m.examination_cost as '检查费用',
        m.treatment_cost as '治疗费用',
        m.nursing_cost as '护理费用',
        m.material_cost as '材料费用',
        m.other_cost as '其他费用',
        m.payment_method as '支付方式',
        m.insurance_number as '医保号',
        CASE WHEN m.is_emergency = 1 THEN '是' ELSE '否' END as '是否急诊'
    FROM medical_records m
    JOIN patients p ON m.patient_id = p.patient_id
    JOIN departments d ON m.dept_id = d.dept_id
    JOIN doctors doc ON m.attending_doctor_id = doc.doctor_id
    """
    
    try:
        # 使用pandas从数据库读取数据
        df = pd.read_sql(query, conn)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"病案首页数据_{timestamp}.xlsx"
        
        # 导出到Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"\n数据导出成功！文件名: {filename}")
        print(f"共导出 {len(df)} 条记录")
        
        return filename
    except Exception as e:
        print(f"导出数据时出错: {e}")
        return None

# 导出患者基本信息
def export_patients(conn):
    # SQL查询语句
    query = """
    SELECT 
        p.patient_name as '姓名',
        p.gender as '性别',
        p.birth_date as '出生日期',
        TIMESTAMPDIFF(YEAR, p.birth_date, CURRENT_DATE()) as '年龄',
        p.id_card as '身份证号',
        p.phone as '联系电话',
        p.address as '家庭住址',
        p.emergency_contact as '紧急联系人',
        p.emergency_phone as '紧急联系电话',
        p.blood_type as '血型',
        p.allergy_history as '过敏史'
    FROM patients p
    """
    
    try:
        # 使用pandas从数据库读取数据
        df = pd.read_sql(query, conn)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"患者基本信息_{timestamp}.xlsx"
        
        # 导出到Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"\n数据导出成功！文件名: {filename}")
        print(f"共导出 {len(df)} 条记录")
        
        return filename
    except Exception as e:
        print(f"导出数据时出错: {e}")
        return None

# 导出住院记录
def export_admissions(conn):
    # SQL查询语句
    query = """
    SELECT 
        p.patient_name as '姓名',
        a.admission_number as '住院号',
        a.admission_date as '入院日期',
        a.discharge_date as '出院日期',
        DATEDIFF(a.discharge_date, a.admission_date) as '住院天数',
        d.dept_name as '科室',
        a.bed_number as '床位号',
        doc.doctor_name as '主治医师',
        a.admission_type as '入院类型',
        a.admission_diagnosis as '入院诊断',
        a.discharge_diagnosis as '出院诊断',
        a.chief_complaint as '主诉',
        a.present_illness as '现病史',
        a.past_history as '既往史',
        a.treatment_plan as '治疗方案',
        a.discharge_summary as '出院小结',
        a.status as '状态'
    FROM admissions a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN departments d ON a.dept_id = d.dept_id
    JOIN doctors doc ON a.attending_doctor_id = doc.doctor_id
    """
    
    try:
        # 使用pandas从数据库读取数据
        df = pd.read_sql(query, conn)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"住院记录_{timestamp}.xlsx"
        
        # 导出到Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"\n数据导出成功！文件名: {filename}")
        print(f"共导出 {len(df)} 条记录")
        
        return filename
    except Exception as e:
        print(f"导出数据时出错: {e}")
        return None

# 主函数
def main():
    try:
        print("="*50)
        print("医院电子病历数据导出脚本")
        print("="*50)
        print("\n该脚本将从数据库导出病案首页数据为Excel格式。\n")
        
        # 获取数据库连接配置
        db_config = get_db_config()
        
        # 连接到MySQL数据库
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset=db_config['charset']
        )
        
        # 显示菜单
        while True:
            print("\n请选择要导出的数据类型：")
            print("1. 病案首页数据")
            print("2. 患者基本信息")
            print("3. 住院记录")
            print("0. 退出")
            
            choice = input("\n请输入选项编号: ")
            
            if choice == "1":
                export_medical_records(conn)
            elif choice == "2":
                export_patients(conn)
            elif choice == "3":
                export_admissions(conn)
            elif choice == "0":
                break
            else:
                print("无效的选项，请重新输入！")
        
    except mysql.connector.Error as err:
        print(f"\n数据库错误: {err}")
    except Exception as e:
        print(f"\n程序错误: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    main() 