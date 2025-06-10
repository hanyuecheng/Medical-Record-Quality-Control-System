import os
import json
import re

# 医学实体配置文件路径
ENTITIES_CONFIG_FILE = 'data/medical_entities.json'

# 默认医学实体字典
DEFAULT_ENTITIES = {
    "疾病": [
        "肺炎", "肺不张", "糖尿病", "高血压", "心脏病", "脑梗", "肝炎", "肾炎", 
        "胃炎", "肠炎", "结核", "白血病", "贫血", "抑郁症", "焦虑症", "痛风", 
        "哮喘", "癫痫", "帕金森", "老年痴呆"
    ],
    "症状": [
        "发热", "咳嗽", "咳痰", "胸痛", "头痛", "头晕", "恶心", "呕吐", 
        "腹痛", "腹泻", "便秘", "乏力", "疲劳", "食欲不振", "失眠", "多梦", 
        "心悸", "气短", "呼吸困难", "水肿"
    ],
    "身体部位": [
        "头部", "颈部", "胸部", "腹部", "背部", "腰部", "臀部", "四肢", 
        "上肢", "下肢", "手部", "足部", "头", "颈", "胸", "腹", "背", 
        "腰", "臀", "肩", "臂", "肘", "腕", "手", "指", "髋", "膝", 
        "踝", "足", "趾", "脑", "心", "肺", "肝", "脾", "胃", "肠", 
        "肾", "膀胱", "子宫", "卵巢", "睾丸", "前列腺", "甲状腺"
    ],
    "药物": [
        "青霉素", "阿莫西林", "头孢", "环丙沙星", "甲硝唑", "布洛芬", 
        "对乙酰氨基酚", "阿司匹林", "硝苯地平", "卡托普利", "氯沙坦", 
        "氨氯地平", "美托洛尔", "辛伐他汀", "阿托伐他汀", "二甲双胍", 
        "格列本脲", "胰岛素", "泼尼松", "地塞米松"
    ]
}

# 初始化医学实体配置文件
def init_medical_entities():
    """初始化医学实体配置文件"""
    if not os.path.exists('data'):
        os.makedirs('data', exist_ok=True)
    
    if not os.path.exists(ENTITIES_CONFIG_FILE):
        with open(ENTITIES_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_ENTITIES, f, ensure_ascii=False, indent=2)

# 获取医学实体
def get_medical_entities():
    """获取医学实体字典"""
    try:
        # 确保配置文件存在
        init_medical_entities()
        
        with open(ENTITIES_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取医学实体配置出错: {str(e)}")
        return DEFAULT_ENTITIES

# 保存医学实体
def save_medical_entities(entities):
    """保存医学实体字典"""
    try:
        if not os.path.exists('data'):
            os.makedirs('data', exist_ok=True)
            
        with open(ENTITIES_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存医学实体配置出错: {str(e)}")
        return False

# 识别文本中的医学实体
def recognize_entities(text, entity_dict=None):
    """
    识别文本中的医学实体
    
    Args:
        text: 待识别的文本
        entity_dict: 医学实体字典，如果为None则使用配置文件中的实体
    
    Returns:
        dict: 识别到的实体字典，按实体类型分组
    """
    if entity_dict is None:
        entity_dict = get_medical_entities()
    
    recognized = {}
    
    # 对每种实体类型进行识别
    for entity_type, entities in entity_dict.items():
        found = []
        for entity in entities:
            # 查找所有匹配
            start = 0
            while True:
                pos = text.find(entity, start)
                if pos == -1:
                    break
                
                # 获取上下文
                context_start = max(0, pos - 10)
                context_end = min(len(text), pos + len(entity) + 10)
                context = text[context_start:context_end]
                
                # 添加到结果中
                found.append({
                    'entity': entity,
                    'position': pos,
                    'context': context
                })
                
                start = pos + len(entity)
        
        if found:
            recognized[entity_type] = found
    
    return recognized 