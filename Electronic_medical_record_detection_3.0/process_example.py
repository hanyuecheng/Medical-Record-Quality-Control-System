import pandas as pd
import os
from text_to_excel import parse_medical_text, save_to_excel

# 示例文本 - 完全匹配图片中的数据，每个字段独立一行
example_text = """住院号：711412
姓名：王洋
性别：未知
年龄：25
入院日期：2023-03-10 00:00:00
出院日期：2023-05-19 00:00:00
住院天数：5
科室：妇产科
主治医师：周医生
主要诊断：肺癌
住院号：764126
姓名：郑磊
性别：未知
年龄：95
入院日期：2023-02-21 00:00:00
出院日期：2023-03-12 00:00:00
住院天数：26
科室：肿瘤科
主治医师：王医生
主要诊断：支气管哮喘"""

def main():
    # 解析文本
    data = parse_medical_text(example_text)
    
    if data:
        print(f"成功解析 {len(data)} 条记录")
        # 保存到Excel
        save_to_excel(data, '示例医疗记录.xlsx')
        
        # 显示解析后的数据
        df = pd.DataFrame(data)
        print("\n解析后的数据预览:")
        print(df)
    else:
        print("未能解析任何记录")

if __name__ == "__main__":
    main() 