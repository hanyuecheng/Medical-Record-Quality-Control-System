# 医疗记录文本转Excel工具

这个工具可以将医疗记录文本解析并转换为Excel文件，支持多种文本格式。

## 功能特点

- 支持多种文本格式（每行一个字段、分号分隔字段、混合格式）
- 自动检测文本格式
- 自动转换数据类型（日期、数字等）
- 可定制输出Excel列顺序
- 支持从文件或控制台输入文本
- 提供简单的命令行界面

## 安装依赖

```bash
pip install pandas openpyxl
```

## 使用方法

### 基本命令行工具

```bash
python medical_text_to_excel.py [-h] [-f FILE] [-o OUTPUT] [-t {auto,line,semicolon}] [-c COLUMNS] [-s]
```

参数说明：
- `-h, --help`：显示帮助信息
- `-f, --file FILE`：输入文本文件路径
- `-o, --output OUTPUT`：输出Excel文件名（默认：医疗记录.xlsx）
- `-t, --type {auto,line,semicolon}`：文本格式类型（默认：auto）
- `-c, --columns COLUMNS`：自定义列顺序，用逗号分隔
- `-s, --simple`：使用简化列（仅包含基本列）

### 高级命令行界面

```bash
python medical_text_converter.py {file,text,example} ...
```

子命令：
- `file`：从文件转换
  ```bash
  python medical_text_converter.py file [-h] [-o OUTPUT] [-t {auto,line,semicolon}] [-s] input_file
  ```
  
- `text`：从控制台输入转换
  ```bash
  python medical_text_converter.py text [-h] [-o OUTPUT] [-t {auto,line,semicolon}] [-s]
  ```
  
- `example`：处理示例数据
  ```bash
  python medical_text_converter.py example [-h] [-o OUTPUT] [-s]
  ```

## 文本格式示例

### 1. 每行一个字段

```
住院号：711412
姓名：王洋
性别：未知
年龄：25
入院日期：2023-03-10 00:00:00
出院日期：2023-05-19 00:00:00
住院天数：5
科室：妇产科
主治医师：周医生
主要诊断：肺癌
```

### 2. 分号分隔字段

```
住院号：764126；姓名：郑磊；性别：未知；年龄：95；入院日期：2023-02-21 00:00:00；出院日期：2023-03-12 00:00:00；住院天数：26；科室：肿瘤科；主治医师：王医生；主要诊断：支气管哮喘；
```

### 3. 混合格式

```
住院号：764127
姓名：李明；性别：男；年龄：45
入院日期：2023-04-15 00:00:00；出院日期：2023-05-01 00:00:00
住院天数：16；科室：心内科；主治医师：张医生
主要诊断：冠心病；次要诊断：高血压；手术名称：冠状动脉搭桥术；手术日期：2023-04-20 00:00:00；费用总额：52680.75。
```

## 示例用法

### 从文件转换

```bash
python medical_text_converter.py file example_data.txt -s
```

### 从控制台输入转换

```bash
python medical_text_converter.py text -s
```

然后输入医疗记录文本，完成后按Ctrl+Z并回车结束输入。

### 处理示例数据

```bash
python medical_text_converter.py example -s
```

## 注意事项

1. 每条记录必须以"住院号："开头
2. 支持的日期格式：YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD
3. 生成的Excel文件保存在excel_data目录下 