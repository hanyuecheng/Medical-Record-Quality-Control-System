# 医院电子病历样本数据生成工具

这个项目提供了用于生成医院电子病历样本数据的工具，可以用于测试、开发和质控检查。

## 文件说明

本项目包含以下主要文件：

1. `hospital_emr_schema.sql` - 医院电子病历数据库结构SQL文件
2. `generate_hospital_data.py` - 基于MySQL数据库的样本数据生成脚本
3. `generate_sample_csv.py` - 生成CSV格式的样本数据脚本（不需要数据库）
4. `generate_sample_excel.py` - 生成Excel格式的样本数据脚本（不需要数据库）
5. `export_medical_records.py` - 从数据库导出病历数据的脚本

## 环境要求

- Python 3.6+
- 相关Python库：
  - MySQL连接：`mysql-connector-python`
  - 数据处理：`pandas`
  - Excel支持：`openpyxl`

可以使用以下命令安装所需依赖：

```bash
pip install mysql-connector-python pandas openpyxl
```

## 使用方法

### 方法一：使用Excel生成器（推荐，无需数据库）

这种方法最简单，直接生成Excel格式的样本数据：

```bash
python generate_sample_excel.py
```

生成的数据将保存在`excel_data/hospital_data.xlsx`文件中，包含以下工作表：
- 科室信息
- 医生信息
- 护士信息
- 患者信息
- 住院记录

### 方法二：使用CSV生成器（无需数据库）

如果需要CSV格式的数据：

```bash
python generate_sample_csv.py
```

生成的CSV文件将保存在`csv_data/`目录下，包含多个CSV文件。

**注意**：CSV文件使用UTF-8-SIG编码，可以正确显示中文字符，包括在Windows系统中打开。

### 方法三：使用MySQL数据库（完整功能）

如果需要在MySQL数据库中创建完整的电子病历系统：

1. 首先确保MySQL服务器已安装并运行
2. 运行数据生成脚本：

```bash
python generate_hospital_data.py
```

3. 按照提示输入数据库连接信息
4. 脚本将创建数据库、表结构并生成样本数据

## 生成的数据

样本数据包括：

- 5个科室信息
- 5个医生信息
- 5个护士信息
- 5个患者基本信息
- 5条住院记录
- 5条病案首页记录（仅CSV和MySQL方式）

## 注意事项

- 生成的数据仅用于测试和开发，不包含真实患者信息
- 如果在旧版本Windows系统下CSV文件仍有中文编码问题，请尝试使用Excel格式
- 在使用MySQL方式时，请确保有足够的数据库权限

## 问题排查

如果遇到问题：

1. 确保已安装所有依赖库
2. 检查Python版本（3.6+）
3. 使用MySQL方式时，确保数据库连接信息正确
4. 如果CSV文件中文显示乱码：
   - 确认使用的是最新版本的脚本（使用UTF-8-SIG编码）
   - 尝试在Excel中打开CSV文件，选择UTF-8编码
   - 或者直接使用Excel生成器替代 