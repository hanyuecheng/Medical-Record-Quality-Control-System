import re
import os
import pandas as pd
from datetime import datetime
import argparse

def parse_medical_text(text, format_type='auto'):
    """
    解析医疗记录文本，提取结构化数据
    
    参数:
    - text: 要解析的文本
    - format_type: 文本格式类型，可选值：'auto'（自动检测）, 'line'（每行一个字段）, 'semicolon'（分号分隔字段）
    
    返回:
    - 解析后的数据列表
    """
    # 预处理：移除注释行（以#开头的行）
    lines = []
    for line in text.split('\n'):
        if not line.strip().startswith('#'):
            lines.append(line)
    text = '\n'.join(lines)
    
    if format_type == 'auto':
        # 尝试使用混合解析方法
        return parse_mixed_format(text)
    elif format_type == 'line':
        return parse_line_format(text)
    else:
        return parse_semicolon_format(text)

def parse_mixed_format(text):
    """混合格式解析"""
    # 首先按住院号分割文本，每个住院号开始一条新记录
    pattern = r'(住院号：\d+)'
    sections = re.split(pattern, text)
    
    # 第一个部分可能是空的
    if not sections[0].strip():
        sections = sections[1:]
    
    # 重组sections，每两个一组（住院号和剩余内容）
    records_text = []
    for i in range(0, len(sections), 2):
        if i+1 < len(sections):
            records_text.append(sections[i] + sections[i+1])
    
    # 解析每条记录
    data = []
    for record_text in records_text:
        record_dict = {}
        
        # 分割行和分号分隔的字段
        lines = record_text.split('\n')
        for line in lines:
            if not line.strip():
                continue
                
            # 处理行中的字段（可能有多个字段用分号分隔）
            fields = line.split('；')
            for field in fields:
                if not field.strip():
                    continue
                    
                parts = field.split('：', 1)
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    field_value = parts[1].strip()
                    
                    # 去掉末尾的句号
                    if field_value.endswith('。'):
                        field_value = field_value[:-1]
                    
                    record_dict[field_name] = field_value
        
        if record_dict:
            data.append(record_dict)
    
    return process_data_types(data)

def parse_line_format(text):
    """每行一个字段的格式解析"""
    lines = text.strip().split('\n')
    lines = [line for line in lines if line.strip()]
    
    data = []
    current_record = {}
    
    for line in lines:
        # 如果行以"住院号："开头，表示新记录开始
        if line.startswith('住院号：'):
            # 如果当前记录不为空，添加到数据列表
            if current_record:
                data.append(current_record)
            # 创建新记录
            current_record = {}
        
        # 提取字段名和值
        parts = line.split('：', 1)
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
        
    return process_data_types(data)

def parse_semicolon_format(text):
    """分号分隔字段的格式解析"""
    # 分割每条记录
    records = text.strip().split('。\n')
    if len(records) == 1:
        records = text.strip().split('\n')
    
    data = []
    
    for record in records:
        # 跳过空记录
        if not record or record == '。':
            continue
            
        # 提取所有字段
        record_dict = {}
        fields = record.split('；')
        
        for field in fields:
            if not field.strip():
                continue
                
            parts = field.split('：', 1)
            if len(parts) == 2:
                field_name = parts[0].strip()
                field_value = parts[1].strip()
                
                # 去掉末尾的句号
                if field_value.endswith('。'):
                    field_value = field_value[:-1]
                
                record_dict[field_name] = field_value
        
        if record_dict:
            data.append(record_dict)
    
    return process_data_types(data)

def process_data_types(data):
    """处理数据类型转换"""
    for record in data:
        # 处理日期格式
        for date_field in ['入院日期', '出院日期', '手术日期']:
            if date_field in record and record[date_field]:
                try:
                    # 处理不同的日期格式
                    date_str = record[date_field].replace('/', '-')
                    # 尝试不同的日期格式
                    date_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
                    for fmt in date_formats:
                        try:
                            dt = datetime.strptime(date_str.strip(), fmt)
                            record[date_field] = dt
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    print(f"日期格式转换错误: {record[date_field]} - {e}")
        
        # 转换数值字段
        for num_field in ['年龄', '住院天数']:
            if num_field in record and record[num_field]:
                try:
                    record[num_field] = int(record[num_field])
                except ValueError:
                    pass
        
        # 转换费用为浮点数
        if '费用总额' in record and record['费用总额']:
            try:
                record['费用总额'] = float(record['费用总额'])
            except ValueError:
                pass
    
    return data

def save_to_excel(data, output_file='医疗记录.xlsx', columns=None):
    """
    将解析后的数据保存为Excel文件
    
    参数:
    - data: 要保存的数据
    - output_file: 输出文件名
    - columns: 列顺序，如果为None则使用默认顺序
    """
    if not data:
        print("没有数据可保存")
        return False
    
    # 默认列顺序
    if columns is None:
        columns = [
            '住院号', '姓名', '性别', '年龄', '入院日期', '出院日期', 
            '住院天数', '科室', '主治医师', '主要诊断', '次要诊断',
            '手术名称', '手术日期', '费用总额'
        ]
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 确保所有列都存在
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    
    # 只保留指定的列，并按顺序排列
    available_columns = [col for col in columns if col in df.columns]
    df = df[available_columns]
    
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
            column_width = max(len(str(col)) * 1.5, 10)
            worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    print(f"数据已保存到: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='将医疗记录文本转换为Excel文件')
    parser.add_argument('-f', '--file', help='输入文本文件路径')
    parser.add_argument('-o', '--output', default='医疗记录.xlsx', help='输出Excel文件名')
    parser.add_argument('-t', '--type', choices=['auto', 'line', 'semicolon'], default='auto', help='文本格式类型')
    parser.add_argument('-c', '--columns', help='自定义列顺序，用逗号分隔')
    parser.add_argument('-s', '--simple', action='store_true', help='使用简化列（仅包含图片中显示的列）')
    
    args = parser.parse_args()
    
    # 获取文本内容
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"读取文件出错: {e}")
            return
    else:
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
    
    # 解析自定义列顺序
    columns = None
    if args.columns:
        columns = [col.strip() for col in args.columns.split(',')]
    elif args.simple:
        # 使用简化列（仅包含图片中显示的列）
        columns = [
            '住院号', '姓名', '性别', '年龄', '入院日期', '出院日期', 
            '住院天数', '科室', '主治医师', '主要诊断'
        ]
    
    # 解析文本
    data = parse_medical_text(text, args.type)
    
    if data:
        print(f"成功解析 {len(data)} 条记录")
        # 保存到Excel
        save_to_excel(data, args.output, columns)
        
        # 显示解析后的数据预览
        df = pd.DataFrame(data)
        if len(df) > 5:
            print("\n解析后的数据预览 (前5条):")
            print(df.head())
        else:
            print("\n解析后的数据预览:")
            print(df)
    else:
        print("未能解析任何记录")

if __name__ == "__main__":
    main() 