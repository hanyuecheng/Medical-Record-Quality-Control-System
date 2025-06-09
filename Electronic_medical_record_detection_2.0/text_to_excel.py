import re
import os
import pandas as pd
from datetime import datetime

def parse_medical_text(text):
    """解析医疗记录文本，提取结构化数据"""
    # 分割每条记录 - 修改分隔符为换行符或"；\n"
    records = re.split(r'；\n|；$|\n', text.strip())
    records = [r for r in records if r and not r.isspace()]
    
    # 准备数据存储
    data = []
    current_record = {}
    
    for record in records:
        # 如果记录以"住院号："开头，表示新记录开始
        if record.startswith('住院号：'):
            # 如果当前记录不为空，添加到数据列表
            if current_record:
                data.append(current_record)
            # 创建新记录
            current_record = {}
        
        # 提取字段名和值
        parts = record.split('：', 1)
        if len(parts) == 2:
            field_name = parts[0].strip()
            field_value = parts[1].strip()
            
            # 去掉末尾的分号
            if field_value.endswith('；'):
                field_value = field_value[:-1]
            
            current_record[field_name] = field_value
    
    # 添加最后一条记录
    if current_record:
        data.append(current_record)
    
    # 处理日期和数值字段
    for record in data:
        # 处理日期格式
        for date_field in ['入院日期', '出院日期']:
            if date_field in record and record[date_field]:
                try:
                    dt = datetime.strptime(record[date_field].strip(), '%Y-%m-%d %H:%M:%S')
                    record[date_field] = dt
                except Exception as e:
                    print(f"日期格式转换错误: {record[date_field]} - {e}")
        
        # 转换年龄和住院天数为数字
        for num_field in ['年龄', '住院天数']:
            if num_field in record and record[num_field]:
                try:
                    record[num_field] = int(record[num_field])
                except ValueError:
                    pass
    
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