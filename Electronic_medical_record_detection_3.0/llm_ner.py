"""
基于通用领域大模型的命名实体识别模块
"""
import os
import json
import re
from collections import Counter

# 尝试导入大模型相关库
TRANSFORMER_AVAILABLE = False

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, BertTokenizer, BertForTokenClassification
    TRANSFORMER_AVAILABLE = True
except ImportError:
    print("警告: transformers 或 torch 库未安装，Transformer模型功能将不可用")

# 配置文件路径
LLM_CONFIG_FILE = 'data/llm_config.json'

# 默认配置
DEFAULT_CONFIG = {
    "model_name": "shibing624/medical-ner",  # 默认使用的预训练模型
    "use_gpu": False,                      # 是否使用GPU
    "offline_mode": True,                  # 是否使用离线模式
    "medical_entity_types": {              # 医学实体类型映射
        "DISEASE": "疾病",
        "SYMPTOM": "症状",
        "BODY": "身体部位",
        "TREATMENT": "治疗",
        "TEST": "检查",
        "DRUG": "药物"
    },
    "custom_entity_types": {               # 自定义实体类型映射
        "PER": "人名",
        "ORG": "组织",
        "LOC": "地点",
        "MISC": "其他",
        "PERSON": "人名",
        "NORP": "国家/政治/宗教",
        "FAC": "设施",
        "ORG": "组织",
        "GPE": "地理政治实体",
        "LOC": "位置",
        "PRODUCT": "产品",
        "EVENT": "事件",
        "WORK_OF_ART": "艺术作品",
        "LAW": "法律",
        "LANGUAGE": "语言",
        "DATE": "日期",
        "TIME": "时间",
        "PERCENT": "百分比",
        "MONEY": "货币",
        "QUANTITY": "数量",
        "ORDINAL": "序数",
        "CARDINAL": "基数"
    }
}

# 简单的医学实体规则
MEDICAL_ENTITY_RULES = {
    "疾病": [
        r"(?<![一-龥])(急性|慢性)?([一-龥]{1,7})(炎|癌|病|瘤|综合征|感染|中毒|梗死|出血|衰竭|损伤|畸形|结石|狭窄|破裂|梗阻|积液|栓塞)(?![一-龥])",
        r"(?<![一-龥])(肺炎|肺不张|糖尿病|高血压|心脏病|脑梗|肝炎|肾炎|胃炎|肠炎|结核|白血病|贫血|抑郁症|焦虑症|痛风|哮喘|癫痫|帕金森|老年痴呆)(?![一-龥])"
    ],
    "症状": [
        r"(?<![一-龥])([一-龥]{1,7})(疼痛|麻痹|麻痺|不畅|不适|肿胀|水肿|恶心|呕吐|腹泻|便秘|头痛|头晕|乏力|疲劳|发热|发烧|咳嗽|咳痰|胸闷|气短|呼吸困难|心悸|心慌|失眠|多梦|食欲不振)(?![一-龥])",
        r"(?<![一-龥])(呼吸不畅|气促|气喘|气急|气短|气粗|气弱|气虚)(?![一-龥])"
    ],
    "身体部位": [
        r"(?<![一-龥])(头部|颈部|胸部|腹部|背部|腰部|臀部|四肢|上肢|下肢|手部|足部|头|颈|胸|腹|背|腰|臀|肩|臂|肘|腕|手|指|髋|膝|踝|足|趾|脑|心|肺|肝|脾|胃|肠|肾|膀胱|子宫|卵巢|睾丸|前列腺|甲状腺|胰腺|胆囊|胆管|食管|气管|支气管|血管|神经|肌肉|骨骼|关节|韧带|软骨|椎间盘|脊髓|脊柱|椎体|颅骨|眼|耳|鼻|口|舌|牙|喉|咽|扁桃体|声带|会厌|气道|呼吸道|消化道|泌尿道|生殖道|呼吸肌|呼吸中枢)(?![一-龥])",
    ],
    "治疗": [
        r"(?<![一-龥])([一-龥]{1,7})(治疗|手术|疗法|用药|处方|处置|干预|调理|康复|护理|照护|保健|预防|预后|随访|复查|复诊|会诊|转诊|转院|出院|住院|入院|急诊|门诊|就诊|诊断|诊治|诊疗|医治|医疗|医护|医嘱)(?![一-龥])",
    ],
    "检查": [
        r"(?<![一-龥])([一-龥]{1,7})(检查|化验|测定|测量|测试|筛查|筛选|评估|评价|监测|监控|观察|观测)(?![一-龥])",
        r"(?<![一-龥])(CT|MRI|B超|X光|超声|核磁|造影|内镜|胃镜|肠镜|支气管镜|膀胱镜|宫腔镜|腹腔镜|关节镜|脑电图|心电图|肌电图|脑血流图)(?![一-龥])",
    ],
    "药物": [
        r"(?<![一-龥])([一-龥]{1,7})(药|剂|片|丸|胶囊|注射液|滴剂|糖浆|冲剂|颗粒|散剂|膏剂|栓剂|贴剂|喷剂|气雾剂|雾化液|溶液|混悬液|乳剂|软膏|凝胶|霜剂)(?![一-龥])",
    ]
}

# 特定医学实体词典
MEDICAL_ENTITY_DICT = {
    "疾病": ["肺炎", "肺不张", "糖尿病", "高血压", "心脏病", "脑梗", "肝炎", "肾炎", "胃炎", "肠炎", "结核", "白血病", "贫血", "抑郁症", "焦虑症", "痛风", "哮喘", "癫痫", "帕金森", "老年痴呆"],
    "症状": ["呼吸不畅", "呼吸肌麻痹", "气促", "气喘", "气急", "气短", "气粗", "气弱", "气虚", "头痛", "头晕", "乏力", "疲劳", "发热", "发烧", "咳嗽", "咳痰", "胸闷", "心悸", "心慌", "失眠", "多梦", "食欲不振"],
    "身体部位": ["头部", "颈部", "胸部", "腹部", "背部", "腰部", "臀部", "四肢", "上肢", "下肢", "手部", "足部", "头", "颈", "胸", "腹", "背", "腰", "臀", "肩", "臂", "肘", "腕", "手", "指", "髋", "膝", "踝", "足", "趾", "脑", "心", "肺", "肝", "脾", "胃", "肠", "肾", "膀胱", "子宫", "卵巢", "睾丸", "前列腺", "甲状腺", "胰腺", "胆囊", "胆管", "食管", "气管", "支气管", "血管", "神经", "肌肉", "骨骼", "关节", "韧带", "软骨", "椎间盘", "脊髓", "脊柱", "椎体", "颅骨", "眼", "耳", "鼻", "口", "舌", "牙", "喉", "咽", "扁桃体", "声带", "会厌", "气道", "呼吸道", "消化道", "泌尿道", "生殖道", "呼吸肌", "呼吸中枢"],
}

# 初始化配置文件
def init_config():
    """初始化LLM配置文件"""
    if not os.path.exists('data'):
        os.makedirs('data', exist_ok=True)
    
    if not os.path.exists(LLM_CONFIG_FILE):
        with open(LLM_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)

# 获取LLM配置
def get_llm_config():
    """获取LLM配置"""
    try:
        with open(LLM_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取LLM配置文件出错: {str(e)}")
        return DEFAULT_CONFIG

# 保存LLM配置
def save_llm_config(config):
    """保存LLM配置"""
    try:
        with open(LLM_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存LLM配置文件出错: {str(e)}")

# 加载Transformer模型
def load_transformer_model(model_name=None):
    """
    加载Transformer模型
    
    Args:
        model_name: 模型名称，如果为None则使用配置文件中的模型
    
    Returns:
        NER pipeline
    """
    if not TRANSFORMER_AVAILABLE:
        print("Transformer模型不可用，请安装transformers和torch库")
        return None
        
    config = get_llm_config()
    if model_name is None:
        model_name = config["model_name"]
    
    use_gpu = config["use_gpu"] and torch.cuda.is_available()
    device = 0 if use_gpu else -1
    offline_mode = config.get("offline_mode", False)
    
    try:
        if offline_mode:
            # 使用规则匹配替代模型
            print(f"使用离线模式，将使用规则匹配替代模型")
            return "RULE_BASED"
        else:
            print(f"加载模型: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForTokenClassification.from_pretrained(model_name)
            ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, device=device)
            return ner_pipeline
    except Exception as e:
        print(f"加载Transformer模型出错: {str(e)}")
        print("将使用规则匹配替代模型")
        return "RULE_BASED"

# 使用词典匹配进行医学实体识别
def recognize_entities_with_dict(text):
    """
    使用词典匹配进行医学实体识别
    
    Args:
        text: 待识别的文本
        
    Returns:
        dict: 识别到的实体字典，按实体类型分组
    """
    entities_by_type = {}
    
    # 对每种实体类型应用词典匹配
    for entity_type, words in MEDICAL_ENTITY_DICT.items():
        entities = []
        for word in words:
            # 查找所有匹配位置
            start = 0
            while True:
                position = text.find(word, start)
                if position == -1:
                    break
                
                # 获取上下文
                context_start = max(0, position - 10)
                context_end = min(len(text), position + len(word) + 10)
                context = text[context_start:context_end]
                
                # 检查是否已存在相同实体
                if not any(e['entity'] == word and e['position'] == position for e in entities):
                    entities.append({
                        'entity': word,
                        'position': position,
                        'context': context
                    })
                
                start = position + len(word)
        
        if entities:
            entities_by_type[entity_type] = entities
    
    return entities_by_type

# 使用规则匹配进行医学实体识别
def recognize_entities_with_rules(text):
    """
    使用规则匹配进行医学实体识别
    
    Args:
        text: 待识别的文本
        
    Returns:
        dict: 识别到的实体字典，按实体类型分组
    """
    # 先使用词典匹配
    entities_by_type = recognize_entities_with_dict(text)
    
    # 再使用规则匹配补充
    for entity_type, patterns in MEDICAL_ENTITY_RULES.items():
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
            
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                entity_text = match.group(0)
                position = match.start()
                
                # 获取上下文
                context_start = max(0, position - 10)
                context_end = min(len(text), position + len(entity_text) + 10)
                context = text[context_start:context_end]
                
                # 检查是否已存在相同实体
                if not any(e['entity'] == entity_text and e['position'] == position for e in entities_by_type[entity_type]):
                    entities_by_type[entity_type].append({
                        'entity': entity_text,
                        'position': position,
                        'context': context
                    })
    
    return entities_by_type

# 使用Transformer模型进行命名实体识别
def recognize_entities_with_transformer(text, model_name=None):
    """
    使用Transformer模型进行命名实体识别
    
    Args:
        text: 待识别的文本
        model_name: 模型名称，如果为None则使用配置文件中的模型
    
    Returns:
        dict: 识别到的实体字典，按实体类型分组
    """
    if not TRANSFORMER_AVAILABLE:
        print("Transformer模型不可用，请安装transformers和torch库")
        return {"未安装依赖": [{"entity": "请安装transformers和torch库", "position": 0, "context": "系统检测到未安装必要的依赖库"}]}
    
    ner_pipeline = load_transformer_model(model_name)
    
    # 如果返回RULE_BASED，使用规则匹配
    if ner_pipeline == "RULE_BASED":
        return recognize_entities_with_rules(text)
    
    if ner_pipeline is None:
        return {"模型加载失败": [{"entity": "请检查模型配置", "position": 0, "context": "系统无法加载指定的Transformer模型"}]}
    
    config = get_llm_config()
    custom_entity_types = config["custom_entity_types"]
    
    try:
        # 分段处理长文本，避免超出模型最大长度限制
        max_length = 512
        segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        all_entities = []
        offset = 0
        for segment in segments:
            entities = ner_pipeline(segment)
            # 调整位置偏移
            for entity in entities:
                entity['start'] += offset
                entity['end'] += offset
            all_entities.extend(entities)
            offset += len(segment)
        
        # 合并相邻相同类型的实体
        merged_entities = []
        current_entity = None
        
        for entity in all_entities:
            if current_entity is None:
                current_entity = entity.copy()
            elif (entity['entity'] == current_entity['entity'] and 
                  entity['start'] <= current_entity['end'] + 1):
                # 合并相邻实体
                current_entity['end'] = entity['end']
                current_entity['word'] = text[current_entity['start']:current_entity['end']]
                current_entity['score'] = max(current_entity['score'], entity['score'])
            else:
                merged_entities.append(current_entity)
                current_entity = entity.copy()
        
        if current_entity is not None:
            merged_entities.append(current_entity)
        
        # 按实体类型分组
        entities_by_type = {}
        for entity in merged_entities:
            entity_type = entity['entity'].split('-')[-1]  # 去除B-、I-前缀
            entity_text = text[entity['start']:entity['end']]
            
            # 映射实体类型
            mapped_type = custom_entity_types.get(entity_type, entity_type)
            
            if mapped_type not in entities_by_type:
                entities_by_type[mapped_type] = []
            
            # 获取上下文
            context_start = max(0, entity['start'] - 10)
            context_end = min(len(text), entity['end'] + 10)
            context = text[context_start:context_end]
            
            entities_by_type[mapped_type].append({
                'entity': entity_text,
                'position': entity['start'],
                'context': context,
                'score': round(entity['score'], 3)
            })
        
        # 如果在线模型没有识别到实体，尝试使用规则匹配
        if not entities_by_type:
            print("在线模型未识别到实体，尝试使用规则匹配替代")
            return recognize_entities_with_rules(text)
            
        return entities_by_type
    
    except Exception as e:
        print(f"Transformer实体识别出错: {str(e)}")
        print("尝试使用规则匹配替代")
        return recognize_entities_with_rules(text)

# 统计实体频率
def calculate_entity_statistics(recognized_entities):
    """
    计算实体统计信息
    
    Args:
        recognized_entities: 识别到的实体字典
    
    Returns:
        dict: 实体统计信息
    """
    entity_statistics = {}
    
    for entity_type, entities in recognized_entities.items():
        # 统计每个实体的出现次数
        entity_counts = Counter([entity_info['entity'] for entity_info in entities])
        entity_statistics[entity_type] = dict(entity_counts)
    
    return entity_statistics

# 初始化配置
init_config() 