from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话安全的密钥，生产环境应使用强随机密钥

# 创建必要的存储目录
os.makedirs('data', exist_ok=True)    # 用于存储规则和映射数据
os.makedirs('uploads', exist_ok=True)  # 用于存储上传的文件

# 文件路径常量定义
RULES_FILE = 'data/rules.json'  # 规则文件路径
DIAGNOSIS_DEPT_MAPPING_FILE = 'data/diagnosis_department_mapping.json'  # 科室与诊断映射文件路径

# 初始化规则文件（如果不存在）
if not os.path.exists(RULES_FILE):
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)

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

# 检查页面
@app.route('/check')
def check_page():
    """数据检查页面路由，显示文件上传界面"""
    return render_template('check.html')

# 清理DataFrame中的非JSON兼容数据
def clean_dataframe_for_json(df):
    """
    清理DataFrame中不能被JSON序列化的数据类型
    
    Args:
        df (DataFrame): 需要清理的DataFrame
        
    Returns:
        dict: 清理后的数据字典，可以安全地序列化为JSON
    """
    # 创建DataFrame的副本
    df_clean = df.copy()
    
    # 替换NaT和NaN值
    df_clean = df_clean.replace({pd.NaT: None})
    df_clean = df_clean.replace({np.nan: None})
    
    # 处理非原生Python类型
    for col in df_clean.columns:
        # 转换日期时间类型为字符串
        if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].astype(str).where(~df_clean[col].isna(), None)
        
        # 确保整数类型正确转换
        elif pd.api.types.is_integer_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].astype('Int64').where(~df_clean[col].isna(), None)
        
        # 其他数值类型转换为浮点数
        elif pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].astype(float).where(~df_clean[col].isna(), None)
    
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
    return send_from_directory('uploads', filename, as_attachment=True)

# 应用入口
if __name__ == '__main__':
    app.run(debug=True)  # 生产环境应设置debug=False 