#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
医疗记录文本转Excel工具

这个脚本提供了一个简单的命令行界面，用于将医疗记录文本转换为Excel文件。
"""

import os
import sys
import argparse
from medical_text_to_excel import parse_medical_text, save_to_excel

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='医疗记录文本转Excel工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 文件转换子命令
    file_parser = subparsers.add_parser('file', help='从文件转换')
    file_parser.add_argument('input_file', help='输入文本文件路径')
    file_parser.add_argument('-o', '--output', help='输出Excel文件名')
    file_parser.add_argument('-t', '--type', choices=['auto', 'line', 'semicolon'], default='auto', help='文本格式类型')
    file_parser.add_argument('-s', '--simple', action='store_true', help='使用简化列（仅包含基本列）')
    
    # 文本输入子命令
    text_parser = subparsers.add_parser('text', help='从控制台输入转换')
    text_parser.add_argument('-o', '--output', help='输出Excel文件名')
    text_parser.add_argument('-t', '--type', choices=['auto', 'line', 'semicolon'], default='auto', help='文本格式类型')
    text_parser.add_argument('-s', '--simple', action='store_true', help='使用简化列（仅包含基本列）')
    
    # 示例子命令
    example_parser = subparsers.add_parser('example', help='处理示例数据')
    example_parser.add_argument('-o', '--output', default='示例医疗记录.xlsx', help='输出Excel文件名')
    example_parser.add_argument('-s', '--simple', action='store_true', help='使用简化列（仅包含基本列）')
    
    args = parser.parse_args()
    
    # 如果没有指定子命令，显示帮助信息
    if not args.command:
        parser.print_help()
        return
    
    # 确定列顺序
    columns = None
    if getattr(args, 'simple', False):
        # 使用简化列（仅包含基本列）
        columns = [
            '住院号', '姓名', '性别', '年龄', '入院日期', '出院日期', 
            '住院天数', '科室', '主治医师', '主要诊断'
        ]
    
    # 处理文件转换子命令
    if args.command == 'file':
        # 读取文件内容
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"读取文件出错: {e}")
            return
        
        # 确定输出文件名
        output_file = args.output if args.output else os.path.splitext(os.path.basename(args.input_file))[0] + '.xlsx'
        
        # 解析文本
        data = parse_medical_text(text, args.type)
        
        if data:
            print(f"成功解析 {len(data)} 条记录")
            # 保存到Excel
            save_to_excel(data, output_file, columns)
        else:
            print("未能解析任何记录")
    
    # 处理文本输入子命令
    elif args.command == 'text':
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
        
        # 确定输出文件名
        output_file = args.output if args.output else '医疗记录.xlsx'
        
        # 解析文本
        data = parse_medical_text(text, args.type)
        
        if data:
            print(f"成功解析 {len(data)} 条记录")
            # 保存到Excel
            save_to_excel(data, output_file, columns)
        else:
            print("未能解析任何记录")
    
    # 处理示例子命令
    elif args.command == 'example':
        # 示例文本
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
        
        # 解析示例文本
        data = parse_medical_text(example_text)
        
        if data:
            print(f"成功解析 {len(data)} 条示例记录")
            # 保存到Excel
            save_to_excel(data, args.output, columns)
        else:
            print("未能解析任何示例记录")

if __name__ == '__main__':
    main() 