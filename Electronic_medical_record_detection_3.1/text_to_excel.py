import re
import os
import pandas as pd
from datetime import datetime

def parse_medical_text(text):
    """
    解析医疗记录文本，提取结构化数据
    
    支持以下格式：
    1. 每行一个字段（字段名：字段值）
    2. 分号分隔字段（字段名：字段值；字段名：字段值；...）
    3. 混合格式
    
    多名患者记录应使用空行分隔
    """
    # 分割每条记录 - 使用空行作为记录分隔符
    records_text = re.split(r'\n\s*\n', text.strip())
    
    # 准备数据存储
    data = []
    
    for record_text in records_text:
        if not record_text.strip():
            continue
            
        # 分割每个字段 - 使用换行符或分号作为字段分隔符
        fields = re.split(r'；\n|；|\n', record_text.strip())
        fields = [f for f in fields if f and not f.isspace()]
        
        # 解析字段
        record = {}
        for field in fields:
            # 提取字段名和值
            parts = field.split('：', 1)
            if len(parts) == 2:
                field_name = parts[0].strip()
                field_value = parts[1].strip()
                
                # 去掉末尾的分号、句号等标点
                field_value = re.sub(r'[；。,，]$', '', field_value)
                
                record[field_name] = field_value
        
        # 添加记录
        if record and '住院号' in record:  # 确保至少有住院号字段
            data.append(record)
    
    return data

def save_to_excel(data, output_file='医疗记录.xlsx'):
    """将解析后的数据保存为Excel文件，格式与图片一致"""
    if not data:
        print("没有数据可保存")
        return False
    
    # 重新排列列顺序，与图片一致
    columns = [
        '住院号', '姓名', '性别', '年龄', '入院日期', '出院日期', 
        '住院天数', '科室', '主治医师', '主要诊断'
    ]
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 确保所有列都存在
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    
    # 重新排序列
    df = df[columns]
    
    # 确保excel_data目录存在
    os.makedirs('excel_data', exist_ok=True)
    
    # 保存到Excel
    output_path = os.path.join('excel_data', output_file)
    
    # 使用openpyxl引擎保存，以便后续设置格式
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        # 获取工作簿和工作表对象
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # 设置列宽
        for i, col in enumerate(df.columns):
            column_width = max(len(col) * 1.5, 10)
            worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    print(f"数据已保存到: {output_path}")
    return True

def main():
    print("请输入医疗记录文本 (输入完成后按Ctrl+Z并回车结束):")
    try:
        text = ""
        while True:
            try:
                line = input()
                text += line + "\n"
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\n输入已取消")
        return
    
    # 解析文本
    data = parse_medical_text(text)
    
    if data:
        print(f"成功解析 {len(data)} 条记录")
        # 保存到Excel
        save_to_excel(data)
    else:
        print("未能解析任何记录")

if __name__ == "__main__":
    main() 