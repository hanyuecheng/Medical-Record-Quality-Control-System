"""
生成示例病案首页数据，用于测试质控系统
"""

import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 创建目录
os.makedirs('sample', exist_ok=True)

# 示例数据生成函数
def generate_sample_data(rows=50):
    # 生成随机日期
    def random_date(start_date, end_date):
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        return start_date + timedelta(days=random_number_of_days)
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    # 姓氏列表
    last_names = ['张', '王', '李', '赵', '陈', '刘', '杨', '黄', '周', '吴', 
                 '郑', '孙', '马', '朱', '胡', '林', '郭', '何', '高', '罗']
    
    # 名字组合
    first_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '洋',
                  '艳', '勇', '军', '杰', '娟', '涛', '明', '超', '秀兰', '霞']
    
    # 科室列表
    departments = ['内科', '外科', '妇产科', '儿科', '神经科', '骨科', '肿瘤科', 
                  '眼科', '耳鼻喉科', '口腔科', '皮肤科', '精神科', '急诊科']
    
    # 诊断列表
    diagnoses = [
        '高血压', '糖尿病', '冠心病', '肺炎', '胃炎', '肝炎', '肾炎', 
        '骨折', '脑梗塞', '脑出血', '贫血', '白血病', '肺癌', '胃癌', 
        '结肠癌', '前列腺炎', '慢性阻塞性肺疾病', '支气管炎', '支气管哮喘',
        '子宫肌瘤', '乳腺增生', '宫颈炎', '前列腺增生', '阑尾炎'
    ]
    
    # 主治医师
    doctors = ['陈医生', '王医生', '李医生', '张医生', '刘医生', 
              '赵医生', '黄医生', '周医生', '吴医生', '郑医生']
    
    # 创建数据字典
    data = {
        '住院号': [f'{random.randint(100000, 999999)}' for _ in range(rows)],
        '姓名': [random.choice(last_names) + random.choice(first_names) for _ in range(rows)],
        '性别': [random.choice(['男', '女', '男', '女', '未知']) for _ in range(rows)],
        '年龄': [random.randint(-1, 99) for _ in range(rows)],  # 故意加入负数作为错误数据
        '入院日期': [random_date(start_date, end_date) for _ in range(rows)],
        '出院日期': [random_date(start_date, end_date) for _ in range(rows)],
        '住院天数': [random.randint(1, 30) for _ in range(rows)],
        '科室': [random.choice(departments) for _ in range(rows)],
        '主治医师': [random.choice(doctors) for _ in range(rows)],
        '主要诊断': [random.choice(diagnoses) for _ in range(rows)],
        '次要诊断': [random.choice(diagnoses) if random.random() > 0.3 else '' for _ in range(rows)],
        '手术名称': [f'手术{random.randint(1, 10)}' if random.random() > 0.6 else '' for _ in range(rows)],
        '手术日期': [random_date(start_date, end_date) if random.random() > 0.6 else pd.NaT for _ in range(rows)],
        '费用总额': [round(random.uniform(1000, 50000), 2) for _ in range(rows)],
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 故意制造一些缺失值
    for col in ['姓名', '性别', '主要诊断', '科室', '主治医师']:
        mask = np.random.random(size=rows) < 0.1  # 10%的概率缺失
        df.loc[mask, col] = ''
    
    # 确保一些出院日期晚于入院日期
    for i in range(rows):
        if df.loc[i, '出院日期'] < df.loc[i, '入院日期']:
            df.loc[i, '出院日期'] = df.loc[i, '入院日期'] + timedelta(days=random.randint(1, 30))
    
    # 故意制造一些出院日期早于入院日期的错误
    error_indices = random.sample(range(rows), int(rows * 0.1))  # 10%的错误率
    for i in error_indices:
        df.loc[i, '出院日期'] = df.loc[i, '入院日期'] - timedelta(days=random.randint(1, 10))
    
    # 故意制造性别与科室不匹配的错误
    # 男性不应该在妇产科就诊
    male_indices = df[df['性别'] == '男'].index.tolist()
    if male_indices:
        error_count = min(5, len(male_indices))  # 最多5个错误
        for i in random.sample(male_indices, error_count):
            df.loc[i, '科室'] = '妇产科'
    
    # 女性不应该有前列腺相关疾病
    female_indices = df[df['性别'] == '女'].index.tolist()
    if female_indices:
        error_count = min(5, len(female_indices))  # 最多5个错误
        for i in random.sample(female_indices, error_count):
            df.loc[i, '主要诊断'] = '前列腺增生'
    
    # 故意制造年龄与科室不匹配的错误
    # 成年人不应该在儿科就诊
    adult_indices = df[df['年龄'] >= 18].index.tolist()
    if adult_indices:
        error_count = min(5, len(adult_indices))  # 最多5个错误
        for i in random.sample(adult_indices, error_count):
            df.loc[i, '科室'] = '儿科'
    
    # 儿童不应该在某些成人专科就诊
    child_indices = df[df['年龄'] < 18].index.tolist()
    if child_indices:
        error_count = min(5, len(child_indices))  # 最多5个错误
        adult_departments = ['神经科', '骨科', '精神科']
        for i in random.sample(child_indices, error_count):
            df.loc[i, '科室'] = random.choice(adult_departments)
    
    return df

# 生成示例数据
df = generate_sample_data(50)

# 保存为Excel文件
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
df.to_excel(f'sample/病案首页示例数据_{timestamp}.xlsx', index=False)

print(f"示例数据已生成到 sample/病案首页示例数据_{timestamp}.xlsx") 