from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
from medical_text_to_excel import parse_medical_text, save_to_excel
import mysql.connector
import getpass
import sys
from export_medical_records import export_medical_records, export_patients, export_admissions

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话安全的密钥，生产环境应使用强随机密钥

# 创建必要的存储目录
os.makedirs('data', exist_ok=True)    # 用于存储规则和映射数据
os.makedirs('uploads', exist_ok=True)  # 用于存储上传的文件
os.makedirs('excel_data', exist_ok=True)  # 用于存储生成的Excel文件

# 文件路径常量定义
RULES_FILE = 'data/rules.json'  # 规则文件路径
DIAGNOSIS_DEPT_MAPPING_FILE = 'data/diagnosis_department_mapping.json'  # 科室与诊断映射文件路径
MEDICAL_ENTITIES_FILE = 'data/medical_entities.json'  # 医学实体字典文件路径
DB_CONFIG_FILE = 'data/db_config.json'  # 数据库配置文件路径

# 初始化规则文件（如果不存在）
if not os.path.exists(RULES_FILE):
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)

# 初始化医学实体字典文件（如果不存在）
if not os.path.exists(MEDICAL_ENTITIES_FILE):
    medical_entities = {
        "疾病": ["肺癌", "支气管哮喘", "冠心病", "高血压", "糖尿病", "肝炎", "肺炎"],
        "症状": ["发热", "咳嗽", "胸痛", "头痛", "腹痛", "呕吐", "腹泻"],
        "检查": ["血常规", "尿常规", "肝功能", "CT检查", "核磁共振", "X光检查", "超声检查"],
        "治疗": ["手术", "药物治疗", "放疗", "化疗", "物理治疗", "心理治疗", "康复治疗"],
        "药物": ["青霉素", "阿莫西林", "头孢", "阿司匹林", "布洛芬", "泼尼松", "胰岛素"]
    }
    with open(MEDICAL_ENTITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(medical_entities, ensure_ascii=False, indent=2, fp=f)

# 初始化数据库配置文件（如果不存在）
if not os.path.exists(DB_CONFIG_FILE):
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'hospital_emr',
        'charset': 'utf8mb4'
    }
    with open(DB_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(db_config, ensure_ascii=False, indent=2, fp=f)

# 获取所有规则
def get_rules():
    """
    从规则文件中读取所有质控规则
    
    Returns:
        list: 质控规则列表，如果文件不存在或格式错误则返回空列表
    """
    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取规则文件出错: {str(e)}")
        return []

# 保存规则
def save_rules(rules):
    """
    将规则列表保存到规则文件
    
    Args:
        rules (list): 要保存的规则列表
    """
    try:
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules, ensure_ascii=False, indent=2, fp=f)
    except Exception as e:
        print(f"保存规则文件出错: {str(e)}")

# 获取科室与诊断映射
def get_diagnosis_dept_mapping():
    """
    从映射文件中读取科室与诊断的对应关系
    
    Returns:
        dict: 科室与诊断的映射字典，如果文件不存在或格式错误则返回空字典
    """
    try:
        with open(DIAGNOSIS_DEPT_MAPPING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取科室诊断映射文件出错: {str(e)}")
        return {}

# 获取医学实体字典
def get_medical_entities():
    """
    从医学实体字典文件中读取医学实体数据
    
    Returns:
        dict: 医学实体字典，如果文件不存在或格式错误则返回空字典
    """
    try:
        with open(MEDICAL_ENTITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取医学实体字典文件出错: {str(e)}")
        return {}

# 保存医学实体字典
def save_medical_entities(entities):
    """
    将医学实体字典保存到文件
    
    Args:
        entities (dict): 要保存的医学实体字典
    """
    try:
        with open(MEDICAL_ENTITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(entities, ensure_ascii=False, indent=2, fp=f)
    except Exception as e:
        print(f"保存医学实体字典文件出错: {str(e)}")

# 获取数据库配置
def get_db_config():
    """
    从配置文件中读取数据库配置
    
    Returns:
        dict: 数据库配置字典，如果文件不存在或格式错误则返回默认配置
    """
    try:
        with open(DB_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取数据库配置文件出错: {str(e)}")
        return {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'hospital_emr',
            'charset': 'utf8mb4'
        }

# 保存数据库配置
def save_db_config(config):
    """
    将数据库配置保存到文件
    
    Args:
        config (dict): 要保存的数据库配置
    """
    try:
        with open(DB_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, ensure_ascii=False, indent=2, fp=f)
    except Exception as e:
        print(f"保存数据库配置文件出错: {str(e)}")

# 路由定义部分
# 首页
@app.route('/')
def index():
    """首页路由，显示系统欢迎页面"""
    return render_template('index.html')

# 规则管理页面
@app.route('/rules')
def rules_management():
    """规则管理页面路由，显示所有已配置的规则"""
    rules = get_rules()
    return render_template('rules.html', rules=rules)

# 数据库转Excel页面
@app.route('/db_to_excel')
def db_to_excel_page():
    """数据库转Excel页面路由，显示数据库导出界面"""
    return render_template('db_to_excel.html')

# 保存数据库配置
@app.route('/save_db_config', methods=['POST'])
def save_db_config_route():
    """
    保存数据库配置的路由
    """
    try:
        # 获取表单数据
        host = request.form.get('host', 'localhost')
        user = request.form.get('user', 'root')
        password = request.form.get('password', '')
        database = request.form.get('database', 'hospital_emr')
        
        # 创建配置字典
        config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }
        
        # 测试连接
        try:
            conn = mysql.connector.connect(**config)
            conn.close()
        except mysql.connector.Error as err:
            flash(f'数据库连接失败: {err}')
            return redirect(url_for('db_to_excel_page'))
        
        # 保存配置
        save_db_config(config)
        flash('数据库配置保存成功！')
        return redirect(url_for('db_to_excel_page'))
    except Exception as e:
        flash(f'保存数据库配置失败: {str(e)}')
        return redirect(url_for('db_to_excel_page'))

# 导出数据库数据
@app.route('/export_db_data', methods=['POST'])
def export_db_data():
    """
    导出数据库数据的路由
    """
    try:
        # 获取表单数据
        export_type = request.form.get('export_type', 'medical_records')
        
        # 获取数据库配置
        db_config = get_db_config()
        
        # 连接数据库
        try:
            conn = mysql.connector.connect(**db_config)
        except mysql.connector.Error as err:
            flash(f'数据库连接失败: {err}')
            return redirect(url_for('db_to_excel_page'))
        
        # 根据导出类型执行不同的导出函数
        if export_type == 'medical_records':
            filename = export_medical_records(conn)
            title = '病案首页数据'
        elif export_type == 'patients':
            filename = export_patients(conn)
            title = '患者基本信息'
        elif export_type == 'admissions':
            filename = export_admissions(conn)
            title = '住院记录'
        else:
            conn.close()
            flash('不支持的导出类型')
            return redirect(url_for('db_to_excel_page'))
        
        # 关闭连接
        conn.close()
        
        if filename:
            # 移动文件到excel_data目录
            source_path = filename
            target_path = os.path.join('excel_data', filename)
            if os.path.exists(source_path):
                os.rename(source_path, target_path)
            
            # 读取Excel文件并显示预览
            df = pd.read_excel(target_path)
            
            # 处理特殊值
            try:
                # 将NaT（Not a Time）转换为字符串"NaT"
                for col in df.select_dtypes(include=['datetime64']).columns:
                    df[col] = df[col].astype(str).replace('NaT', '')
                    
                # 确保所有对象类型的列都转换为字符串
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype(str)
                
                # 处理数值列
                for col in df.select_dtypes(include=['number']).columns:
                    df[col] = df[col].astype(str)
            except Exception as e:
                print(f"转换数据类型时出错: {str(e)}")
                # 如果出错，尝试将所有列转换为字符串
                for col in df.columns:
                    try:
                        df[col] = df[col].astype(str)
                    except:
                        pass
            
            # 将NaN值替换为空字符串，避免显示"nan"
            df = df.fillna('')
            df = df.replace('nan', '')
            
            # 转换为HTML表格，不显示行索引
            data_html = df.to_html(classes='table table-striped', index=False)
            
            return render_template('db_to_excel_result.html', 
                                title=title,
                                data=data_html, 
                                filename=filename, 
                                record_count=len(df))
        else:
            flash('导出数据失败')
            return redirect(url_for('db_to_excel_page'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"导出数据库数据错误: {str(e)}\n{error_details}")
        flash(f'导出数据库数据错误: {str(e)}')
        return redirect(url_for('db_to_excel_page'))

# 文本转Excel页面
@app.route('/text_to_excel')
def text_to_excel_page():
    """文本转Excel页面路由，显示文本转换界面"""
    return render_template('text_to_excel.html')

# 处理文本转Excel请求
@app.route('/process_text', methods=['POST'])
def process_text():
    """
    处理文本转Excel请求的路由
    解析提交的医疗记录文本，转换为Excel文件
    """
    try:
        # 获取表单数据
        text = request.form.get('text', '')
        format_type = request.form.get('format_type', 'auto')
        use_simple_columns = 'simple_columns' in request.form
        
        if not text:
            flash('请输入医疗记录文本')
            return redirect(url_for('text_to_excel_page'))
        
        # 解析文本
        data = parse_medical_text(text, format_type)
        
        if not data:
            flash('未能解析任何记录')
            return redirect(url_for('text_to_excel_page'))
        
        # 确定列顺序
        columns = None
        if use_simple_columns:
            columns = [
                '住院号', '姓名', '性别', '年龄', '入院日期', '出院日期', 
                '住院天数', '科室', '主治医师', '主要诊断'
            ]
        
        # 生成Excel文件
        filename = f'医疗记录_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        save_to_excel(data, filename, columns)
        
        # 创建DataFrame用于显示
        df = pd.DataFrame(data)
        
        # 确保所有列都存在
        if columns:
            for col in columns:
                if col not in df.columns:
                    df[col] = ''
            # 只保留指定的列，并按顺序排列
            available_columns = [col for col in columns if col in df.columns]
            df = df[available_columns]
        
        # 处理特殊值
        try:
            # 将NaT（Not a Time）转换为字符串"NaT"
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].astype(str).replace('NaT', '')
                
            # 确保所有对象类型的列都转换为字符串
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            
            # 处理数值列
            for col in df.select_dtypes(include=['number']).columns:
                df[col] = df[col].astype(str)
        except Exception as e:
            print(f"转换数据类型时出错: {str(e)}")
            # 如果出错，尝试将所有列转换为字符串
            for col in df.columns:
                try:
                    df[col] = df[col].astype(str)
                except:
                    pass
        
        # 将NaN值替换为空字符串，避免显示"nan"
        df = df.fillna('')
        df = df.replace('nan', '')
        
        # 转换为HTML表格，不显示行索引
        data_html = df.to_html(classes='table table-striped', index=False)
        
        return render_template('text_to_excel_result.html', 
                               data=data_html, 
                               filename=filename, 
                               record_count=len(data))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"文本处理错误: {str(e)}\n{error_details}")
        flash(f'文本处理错误: {str(e)}')
        return redirect(url_for('text_to_excel_page'))

# 医学文本实体识别页面
@app.route('/entity_recognition')
def entity_recognition_page():
    """医学文本实体识别页面路由，显示实体识别界面"""
    entities = get_medical_entities()
    return render_template('entity_recognition.html', entities=entities)

# 处理医学文本实体识别请求
@app.route('/recognize_entities', methods=['POST'])
def recognize_entities():
    """
    处理医学文本实体识别请求的路由
    识别提交文本中的医学实体
    """
    try:
        # 获取表单数据
        text = request.form.get('text', '')
        
        if not text:
            flash('请输入医学文本')
            return redirect(url_for('entity_recognition_page'))
        
        # 获取医学实体字典
        entities_dict = get_medical_entities()
        
        # 识别实体
        recognized_entities = {}
        for entity_type, entity_list in entities_dict.items():
            found_entities = []
            for entity in entity_list:
                if entity in text:
                    # 找出所有匹配位置
                    positions = [m.start() for m in re.finditer(re.escape(entity), text)]
                    for pos in positions:
                        found_entities.append({
                            'entity': entity,
                            'position': pos,
                            'context': text[max(0, pos-10):min(len(text), pos+len(entity)+10)]
                        })
            if found_entities:
                recognized_entities[entity_type] = found_entities
        
        # 准备高亮显示的文本
        highlighted_text = text
        for entity_type, entities in recognized_entities.items():
            for entity_info in sorted(entities, key=lambda x: x['position'], reverse=True):
                entity = entity_info['entity']
                pos = entity_info['position']
                highlighted_text = (
                    highlighted_text[:pos] + 
                    f'<span class="entity-highlight {entity_type.lower()}" title="{entity_type}">{entity}</span>' + 
                    highlighted_text[pos+len(entity):]
                )
        
        return render_template('entity_recognition_result.html', 
                               original_text=text,
                               highlighted_text=highlighted_text,
                               recognized_entities=recognized_entities)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"实体识别错误: {str(e)}\n{error_details}")
        flash(f'实体识别错误: {str(e)}')
        return redirect(url_for('entity_recognition_page'))

# 添加医学实体
@app.route('/add_entity', methods=['POST'])
def add_entity():
    """
    添加新医学实体的路由
    """
    try:
        entity_type = request.form.get('entity_type')
        entity_name = request.form.get('entity_name')
        
        if not entity_type or not entity_name:
            flash('实体类型和名称不能为空')
            return redirect(url_for('entity_recognition_page'))
        
        # 获取现有实体
        entities = get_medical_entities()
        
        # 如果实体类型不存在，创建新类型
        if entity_type not in entities:
            entities[entity_type] = []
        
        # 如果实体名称不存在，添加到列表
        if entity_name not in entities[entity_type]:
            entities[entity_type].append(entity_name)
            save_medical_entities(entities)
            flash(f'成功添加实体: {entity_name} (类型: {entity_type})')
        else:
            flash(f'实体已存在: {entity_name} (类型: {entity_type})')
        
        return redirect(url_for('entity_recognition_page'))
    except Exception as e:
        flash(f'添加实体失败: {str(e)}')
        return redirect(url_for('entity_recognition_page'))

# 删除医学实体
@app.route('/delete_entity', methods=['POST'])
def delete_entity():
    """
    删除医学实体的路由
    """
    try:
        entity_type = request.form.get('entity_type')
        entity_name = request.form.get('entity_name')
        
        if not entity_type or not entity_name:
            flash('实体类型和名称不能为空')
            return redirect(url_for('entity_recognition_page'))
        
        # 获取现有实体
        entities = get_medical_entities()
        
        # 如果实体类型存在且实体名称存在，删除实体
        if entity_type in entities and entity_name in entities[entity_type]:
            entities[entity_type].remove(entity_name)
            save_medical_entities(entities)
            flash(f'成功删除实体: {entity_name} (类型: {entity_type})')
        else:
            flash(f'实体不存在: {entity_name} (类型: {entity_type})')
        
        return redirect(url_for('entity_recognition_page'))
    except Exception as e:
        flash(f'删除实体失败: {str(e)}')
        return redirect(url_for('entity_recognition_page'))

# 检查页面
@app.route('/check')
def check_page():
    """检查页面路由，显示数据上传和检查界面"""
    return render_template('check.html')

# 清理DataFrame以便JSON序列化
def clean_dataframe_for_json(df):
    """
    清理DataFrame以便JSON序列化，处理特殊值如NaT、NaN等
    
    Args:
        df (DataFrame): 要清理的DataFrame
        
    Returns:
        list: 清理后的数据记录列表
    """
    # 创建DataFrame的副本，避免修改原始数据
    df_clean = df.copy()
    
    # 将NaT（Not a Time）转换为None
    for col in df_clean.select_dtypes(include=['datetime64']).columns:
        df_clean[col] = df_clean[col].astype(object).where(~df_clean[col].isna(), None)
    
    # 将NaN转换为None
    df_clean = df_clean.where(pd.notnull(df_clean), None)
    
    # 转换为字典
    return df_clean.to_dict(orient='records')

# 上传并检查文件
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    处理文件上传和规则检查的路由
    读取上传的Excel文件，执行规则检查，并返回检查结果
    """
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(url_for('check_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件')
        return redirect(url_for('check_page'))
    
    try:
        # 保存上传的文件
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # 读取Excel文件
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            flash('请上传Excel文件（.xlsx或.xls格式）')
            return redirect(url_for('check_page'))
            
        # 确保DataFrame非空
        if df.empty:
            flash('上传的文件不包含任何数据')
            return redirect(url_for('check_page'))
            
        # 执行规则检查
        results = check_rules(df)
        
        # 处理特殊值
        try:
            # 将NaT（Not a Time）转换为字符串"NaT"
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].astype(str).replace('NaT', '')
                
            # 确保所有对象类型的列都转换为字符串
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            
            # 处理数值列
            for col in df.select_dtypes(include=['number']).columns:
                df[col] = df[col].astype(str)
        except Exception as e:
            print(f"转换数据类型时出错: {str(e)}")
            # 如果出错，尝试将所有列转换为字符串
            for col in df.columns:
                try:
                    df[col] = df[col].astype(str)
                except:
                    pass
        
        # 将NaN值替换为空字符串，避免显示"nan"
        df = df.fillna('')
        df = df.replace('nan', '')
        
        # 转换为HTML表格，不显示行索引
        data_html = df.to_html(classes='table table-striped', index=False)
        
        return render_template('results.html', results=results, data=data_html)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"文件处理错误: {str(e)}\n{error_details}")
        flash(f'文件处理错误: {str(e)}')
        return redirect(url_for('check_page'))

# 执行规则检查
def check_rules(data):
    """
    对数据执行所有配置的规则检查
    
    Args:
        data (DataFrame): 要检查的数据DataFrame
        
    Returns:
        list: 检查结果列表，每个结果包含规则信息和错误详情
    """
    rules = get_rules()
    results = []
    
    for rule in rules:
        try:
            rule_type = rule['type']
            message = rule['message']
            
            # 缺项检查
            if rule_type == 'missing':
                field = rule['field']
                condition = rule['condition']
                
                # 跳过数据中不存在的字段
                if field not in data.columns:
                    continue
                    
                # 检查字段是否为空或非空
                mask = data[field].isna() | (data[field] == '')
                if condition == 'equals':  # 等于空
                    errors = data[mask]
                else:  # not_equals，不等于空
                    errors = data[~mask]
                    
            # 逻辑检查
            elif rule_type == 'logic':
                field = rule['field']
                condition = rule['condition']
                value = rule['value']
                
                # 跳过数据中不存在的字段
                if field not in data.columns:
                    continue
                    
                # 根据不同的条件类型执行逻辑检查
                if condition == 'equals':  # 等于
                    mask = data[field] == value
                elif condition == 'not_equals':  # 不等于
                    mask = data[field] != value
                elif condition == 'greater_than':  # 大于
                    # 处理日期或数值比较的情况
                    if value in data.columns:  # 如果value是另一个字段名
                        try:
                            # 尝试将两个字段转换为日期类型进行比较
                            field_dates = pd.to_datetime(data[field], errors='coerce')
                            value_dates = pd.to_datetime(data[value], errors='coerce')
                            mask = field_dates <= value_dates  # 检查field是否小于等于value
                        except:
                            # 如果转换失败，尝试直接比较
                            mask = data[field] <= data[value]
                    else:
                        try:
                            # 尝试将字段转换为数值进行比较
                            mask = pd.to_numeric(data[field], errors='coerce') <= float(value)
                        except:
                            # 如果转换失败，尝试字符串比较
                            mask = data[field].astype(str) <= str(value)
                elif condition == 'less_than':  # 小于
                    if value in data.columns:  # 如果value是另一个字段名
                        try:
                            # 尝试将两个字段转换为日期类型进行比较
                            field_dates = pd.to_datetime(data[field], errors='coerce')
                            value_dates = pd.to_datetime(data[value], errors='coerce')
                            mask = field_dates >= value_dates  # 检查field是否大于等于value
                        except:
                            # 如果转换失败，尝试直接比较
                            mask = data[field] >= data[value]
                    else:
                        try:
                            # 尝试将字段转换为数值进行比较
                            mask = pd.to_numeric(data[field], errors='coerce') >= float(value)
                        except:
                            # 如果转换失败，尝试字符串比较
                            mask = data[field].astype(str) >= str(value)
                elif condition == 'contains':  # 包含
                    mask = data[field].astype(str).str.contains(value)
                elif condition == 'not_contains':  # 不包含
                    mask = ~data[field].astype(str).str.contains(value)
                
                # 根据条件名称判断是否需要反转结果
                if 'not' in condition:
                    errors = data[~mask]
                else:
                    errors = data[mask]
                    
            # 关联逻辑检查
            elif rule_type == 'relation':
                field1 = rule['field1']
                field2 = rule['field2']
                relation = rule['relation']
                value_pairs = rule['value_pairs']
                
                # 跳过数据中不存在的字段
                if field1 not in data.columns or field2 not in data.columns:
                    continue
                
                # 特殊处理：科室与入院诊断匹配
                if (field1 == '科室' and field2 == '入院诊断' and relation == 'match_diagnosis') or \
                   (field1 == '科室' and field2 == '主要诊断' and relation == 'match_diagnosis'):
                    try:
                        # 获取科室与诊断映射
                        dept_diag_mapping = get_diagnosis_dept_mapping()
                        errors = pd.DataFrame()
                        
                        # 遍历每行数据
                        for idx, row in data.iterrows():
                            dept = row[field1]
                            diagnosis = row[field2]
                            
                            # 跳过空值
                            if pd.isna(dept) or pd.isna(diagnosis) or dept == '' or diagnosis == '':
                                continue
                            
                            # 如果科室存在于映射中
                            if dept in dept_diag_mapping:
                                # 检查诊断是否与科室匹配
                                matched = False
                                # 遍历科室对应的诊断列表
                                for valid_diag in dept_diag_mapping[dept]:
                                    # 如果诊断包含有效诊断关键词，则认为匹配
                                    if valid_diag in diagnosis:
                                        matched = True
                                        break
                                
                                # 对于特殊的"外科"，需要进一步细分判断
                                if dept.endswith("外科") and not matched:
                                    # 检查是否匹配其他细分外科
                                    for specific_dept in [d for d in dept_diag_mapping if d.endswith("外科") and d != dept]:
                                        for valid_diag in dept_diag_mapping[specific_dept]:
                                            if valid_diag in diagnosis:
                                                matched = True
                                                break
                                        if matched:
                                            break
                                
                                # 对于肿瘤科，特殊处理肺癌、胃癌等多种癌症情况
                                if not matched and "癌" in diagnosis:
                                    for dept_name, diagnoses in dept_diag_mapping.items():
                                        if any(diag in diagnosis for diag in diagnoses if "癌" in diag):
                                            if dept != dept_name and dept_name != "肿瘤科":
                                                matched = False
                                                break
                                
                                # 如果不匹配，添加到错误结果中
                                if not matched:
                                    errors = pd.concat([errors, data.iloc[[idx]]])
                        
                        # 如果有错误，添加到结果中
                        if len(errors) > 0:
                            result = {
                                'rule_name': rule['name'],
                                'message': message,
                                'error_count': len(errors),
                                'error_indices': errors.index.tolist()
                            }
                            results.append(result)
                        continue
                    except Exception as e:
                        # 出错时继续使用常规处理方式
                        print(f"诊断科室匹配检查出错: {str(e)}")
                        pass
                
                # 特殊处理：年龄>14但挂了儿科
                if field1 == '年龄' and field2 == '科室' and relation == 'not_match':
                    try:
                        # 将年龄转换为数值
                        age_numeric = pd.to_numeric(data[field1], errors='coerce')
                        # 检查年龄>14且科室为儿科的情况
                        mask = (age_numeric > 14) & (data[field2].str.contains('儿科'))
                        if mask.any():
                            errors = data[mask]
                            result = {
                                'rule_name': rule['name'],
                                'message': message,
                                'error_count': len(errors),
                                'error_indices': errors.index.tolist()
                            }
                            results.append(result)
                        continue
                    except Exception as e:
                        # 出错时继续使用常规处理方式
                        print(f"年龄科室匹配检查出错: {str(e)}")
                        pass
                
                # 常规关联逻辑检查处理
                try:
                    # 解析值对列表
                    value_pairs_list = []
                    for pair in value_pairs.strip().split('\n'):
                        if pair.strip():
                            val1, val2 = pair.split('=')
                            value_pairs_list.append((val1.strip(), val2.strip()))
                    
                    # 执行匹配检查
                    if relation == 'match':
                        # 检查字段1和字段2的值是否符合指定的匹配关系
                        errors = pd.DataFrame()
                        for val1, val2 in value_pairs_list:
                            # 找出字段1等于val1但字段2不等于val2的行
                            if ',' in val2:  # 如果val2包含多个可能的值
                                valid_val2s = [v.strip() for v in val2.split(',')]
                                mask = (data[field1] == val1) & (~data[field2].isin(valid_val2s))
                            else:
                                mask = (data[field1] == val1) & (data[field2] != val2)
                            errors = pd.concat([errors, data[mask]])
                    elif relation == 'not_match':
                        # 检查字段1和字段2的值是否不符合指定的匹配关系
                        errors = pd.DataFrame()
                        for val1, val2 in value_pairs_list:
                            # 找出字段1等于val1且字段2等于val2的行
                            if ',' in val2:  # 如果val2包含多个不允许的值
                                valid_val2s = [v.strip() for v in val2.split(',')]
                                mask = (data[field1] == val1) & (data[field2].isin(valid_val2s))
                            else:
                                mask = (data[field1] == val1) & (data[field2] == val2)
                            errors = pd.concat([errors, data[mask]])
                except Exception as e:
                    # 解析值对失败时跳过此规则
                    print(f"解析值对失败: {str(e)}")
                    continue
            
            # 跳过没有错误的规则
            if 'errors' not in locals() or len(errors) == 0:
                continue
                
            # 收集错误信息
            error_indices = errors.index.tolist()
            result = {
                'rule_name': rule['name'],
                'message': message,
                'error_count': len(error_indices),
                'error_indices': error_indices
            }
            results.append(result)
            
        except Exception as e:
            # 捕获规则执行过程中的任何异常，确保一个规则的错误不会影响其他规则
            print(f"规则执行出错 ({rule.get('name', '未命名规则')}): {str(e)}")
            continue
    
    return results

# 导出检查结果为CSV的路由
@app.route('/export_results', methods=['POST'])
def export_results():
    """
    导出检查结果的路由
    将检查结果导出为CSV文件供下载
    """
    try:
        # 从POST数据中获取结果和原始数据
        results_data = request.form.get('results')
        original_data = request.form.get('original_data')
        
        if not results_data or not original_data:
            flash('没有可导出的数据')
            return redirect(url_for('check_page'))
            
        # 解析JSON数据
        results = json.loads(results_data)
        original_df = pd.read_json(original_data, orient='records')
        
        # 创建结果文件名（带时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_filename = f"质控结果_{timestamp}.csv"
        result_path = os.path.join('uploads', result_filename)
        
        # 创建结果DataFrame
        result_df = pd.DataFrame(columns=['规则名称', '错误信息', '错误行号'])
        
        for result in results:
            rule_name = result['rule_name']
            message = result['message']
            for idx in result['error_indices']:
                result_df = pd.concat([result_df, pd.DataFrame({
                    '规则名称': [rule_name],
                    '错误信息': [message],
                    '错误行号': [idx + 1]  # 加1以匹配Excel的行号
                })])
        
        # 保存结果到CSV
        result_df.to_csv(result_path, index=False, encoding='utf-8-sig')
        
        # 返回下载链接
        return jsonify({
            'success': True,
            'filename': result_filename,
            'download_url': url_for('download_file', filename=result_filename)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# 文件下载路由
@app.route('/download/<filename>')
def download_file(filename):
    """
    文件下载路由
    
    Args:
        filename (str): 要下载的文件名
    """
    # 检查文件是否在uploads目录中
    if os.path.exists(os.path.join('uploads', filename)):
        return send_from_directory('uploads', filename, as_attachment=True)
    # 检查文件是否在excel_data目录中
    elif os.path.exists(os.path.join('excel_data', filename)):
        return send_from_directory('excel_data', filename, as_attachment=True)
    else:
        flash(f'文件不存在: {filename}')
        return redirect(url_for('index'))

# 添加规则
@app.route('/rules/add', methods=['POST'])
def add_rule():
    """
    添加新规则的路由
    处理表单提交的规则数据，根据规则类型处理不同的字段
    """
    try:
        rules = get_rules()
        rule_id = datetime.now().strftime('%Y%m%d%H%M%S')
        
        rule_type = request.form.get('type')
        
        # 创建基本规则结构
        new_rule = {
            'id': rule_id,
            'name': request.form.get('name'),
            'type': rule_type,
            'message': request.form.get('message')
        }
        
        # 根据规则类型添加不同的字段
        if rule_type == 'missing':  # 缺项检查
            new_rule.update({
                'field': request.form.get('field'),
                'condition': request.form.get('condition'),
                'value': request.form.get('value')
            })
        elif rule_type == 'logic':  # 逻辑检查
            new_rule.update({
                'field': request.form.get('field'),
                'condition': request.form.get('condition'),
                'value': request.form.get('value')
            })
        elif rule_type == 'relation':  # 关联逻辑检查
            new_rule.update({
                'field1': request.form.get('field1'),
                'field2': request.form.get('field2'),
                'relation': request.form.get('relation'),
                'value_pairs': request.form.get('value_pairs')
            })
        
        rules.append(new_rule)
        save_rules(rules)
        flash('规则添加成功！')
    except Exception as e:
        flash(f'添加规则失败: {str(e)}')
    
    return redirect(url_for('rules_management'))

# 编辑规则
@app.route('/rules/edit/<rule_id>', methods=['POST'])
def edit_rule(rule_id):
    """
    编辑现有规则的路由
    
    Args:
        rule_id (str): 要编辑的规则ID
    """
    try:
        rules = get_rules()
        rule_found = False
        
        for rule in rules:
            if rule['id'] == rule_id:
                rule_found = True
                rule_type = request.form.get('type')
                
                # 更新基本信息
                rule['name'] = request.form.get('name')
                rule['type'] = rule_type
                rule['message'] = request.form.get('message')
                
                # 根据规则类型更新不同的字段
                if rule_type == 'missing':  # 缺项检查
                    rule['field'] = request.form.get('field')
                    rule['condition'] = request.form.get('condition')
                    rule['value'] = request.form.get('value')
                elif rule_type == 'logic':  # 逻辑检查
                    rule['field'] = request.form.get('field')
                    rule['condition'] = request.form.get('condition')
                    rule['value'] = request.form.get('value')
                elif rule_type == 'relation':  # 关联逻辑检查
                    rule['field1'] = request.form.get('field1')
                    rule['field2'] = request.form.get('field2')
                    rule['relation'] = request.form.get('relation')
                    rule['value_pairs'] = request.form.get('value_pairs')
                
                break
        
        if not rule_found:
            flash('规则不存在！')
            return redirect(url_for('rules_management'))
            
        save_rules(rules)
        flash('规则更新成功！')
    except Exception as e:
        flash(f'更新规则失败: {str(e)}')
    
    return redirect(url_for('rules_management'))

# 删除规则
@app.route('/rules/delete/<rule_id>')
def delete_rule(rule_id):
    """
    删除规则的路由
    
    Args:
        rule_id (str): 要删除的规则ID
    """
    try:
        rules = get_rules()
        rules = [rule for rule in rules if rule['id'] != rule_id]
        save_rules(rules)
        flash('规则删除成功！')
    except Exception as e:
        flash(f'删除规则失败: {str(e)}')
    
    return redirect(url_for('rules_management'))

# 应用入口
if __name__ == '__main__':
    app.run(debug=True)  # 生产环境应设置debug=False 