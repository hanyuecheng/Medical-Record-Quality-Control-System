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

# 尝试导入网络请求库
API_AVAILABLE = False
try:
    import requests
    API_AVAILABLE = True
except ImportError:
    print("警告: requests库未安装，API调用功能将不可用")

# 配置文件路径
LLM_CONFIG_FILE = 'data/llm_config.json'

# 默认配置
DEFAULT_CONFIG = {
    "model_name": "dslim/bert-base-NER",  # 默认使用的预训练模型
    "use_gpu": False,                      # 是否使用GPU
    "offline_mode": False,                 # 是否使用离线模式
    "local_model_path": "",                # 本地模型路径，如果设置则优先从本地加载
    "api_mode": False,                     # 是否使用API模式
    "api_type": "deepseek",                # API类型：deepseek或douban
    "api_key": "",                         # API密钥
    "api_url": "",                         # API地址
    "chinese_medical_model": "trueto/medbert-kd-chinese", # 中文医学模型
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
        "GPE": "地理政治实体",
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
    },
    "chinese_medical_entity_types": {      # 中文医学实体类型映射
        "DISEASE": "疾病",
        "SYMPTOM": "症状",
        "BODY": "身体部位",
        "TREATMENT": "治疗",
        "TEST": "检查",
        "DRUG": "药物",
        "ANATOMY": "解剖结构",
        "OPERATION": "手术操作",
        "LABORATORY": "实验室检查"
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
    local_model_path = config.get("local_model_path", "")
    api_mode = config.get("api_mode", False)
    
    try:
        # 检查是否使用API模式
        if api_mode and API_AVAILABLE:
            print(f"使用API模式: {config.get('api_type', 'deepseek')}")
            return "API_MODE"
            
        # 检查是否使用离线模式
        if offline_mode:
            print(f"使用离线模式，将使用规则匹配替代模型")
            return "RULE_BASED"
            
        # 检查是否是中文文本，如果是，使用中文医学模型
        is_chinese_model = "chinese" in model_name.lower() or "med" in model_name.lower() or "zh" in model_name.lower()
        
        print(f"加载模型: {model_name} (Chinese Medical Model: {is_chinese_model})")
        
        # 优先尝试从本地路径加载
        if local_model_path and os.path.exists(local_model_path):
            try:
                print(f"尝试从本地路径加载模型: {local_model_path}")
                # 设置特殊选项以处理Windows路径和更好地处理中文
                tokenizer = AutoTokenizer.from_pretrained(
                    local_model_path,
                    local_files_only=True,
                    use_fast=True,
                    add_prefix_space=True,
                    do_lower_case=False
                )
                model = AutoModelForTokenClassification.from_pretrained(
                    local_model_path,
                    local_files_only=True
                )
                # 配置NER pipeline，设置分组相邻实体
                ner_pipeline = pipeline(
                    "ner", 
                    model=model, 
                    tokenizer=tokenizer, 
                    device=device,
                    aggregation_strategy="simple"  # 合并分段的实体
                )
                return ner_pipeline
            except Exception as e:
                print(f"从本地路径加载模型失败: {str(e)}")
                print("尝试其他方式加载模型")
        
        # 尝试从在线加载模型
        try:
            # 设置本地缓存目录
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            print(f"尝试从在线加载模型，缓存目录: {cache_dir}")
            
            # 对于中文医学模型，可以尝试加载中文医学预训练模型
            if is_chinese_model:
                chinese_medical_model = config.get("chinese_medical_model", "trueto/medbert-kd-chinese")
                print(f"加载中文医学模型: {chinese_medical_model}")
                model_name = chinese_medical_model
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                cache_dir=cache_dir,
                use_fast=True,
                add_prefix_space=True
            )
            model = AutoModelForTokenClassification.from_pretrained(
                model_name, 
                cache_dir=cache_dir
            )
            ner_pipeline = pipeline(
                "ner", 
                model=model, 
                tokenizer=tokenizer, 
                device=device,
                aggregation_strategy="simple"  # 合并分段的实体
            )
            return ner_pipeline
        except Exception as inner_e:
            print(f"在线加载模型失败: {str(inner_e)}")
            print("将使用规则匹配替代模型")
            return "RULE_BASED"
    except Exception as e:
        print(f"加载Transformer模型出错: {str(e)}")
        print("将使用规则匹配替代模型")
        return "RULE_BASED"

# 创建不验证SSL证书的会话
def _create_unverified_session():
    """创建一个不验证SSL证书的请求会话"""
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    
    # 禁用不安全请求的警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    session = requests.Session()
    session.verify = False
    return session

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

# 使用API进行命名实体识别
def recognize_entities_with_api(text):
    """
    使用API进行命名实体识别
    
    Args:
        text: 待识别的文本
    
    Returns:
        dict: 识别到的实体字典，按实体类型分组
    """
    if not API_AVAILABLE:
        print("API功能不可用，请安装requests库")
        return {"API错误": [{"entity": "请安装requests库", "position": 0, "context": "系统检测到未安装必要的依赖库"}]}
    
    config = get_llm_config()
    api_type = config.get("api_type", "deepseek")
    api_key = config.get("api_key", "")
    api_url = config.get("api_url", "")
    
    if not api_key or not api_url:
        print("API配置不完整，请设置api_key和api_url")
        return {"API配置错误": [{"entity": "请设置API密钥和地址", "position": 0, "context": "API配置不完整"}]}
    
    try:
        # 构建API请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 构建提示词
        prompt = f"""请识别以下文本中的医学实体，并返回实体列表，格式为JSON：
{text}

请将结果按照以下实体类型分类：疾病、症状、身体部位、治疗、检查、药物
返回结果示例：
{{
  "疾病": [
    {{"entity": "高血压", "position": 5}}
  ],
  "症状": [
    {{"entity": "头痛", "position": 10}},
    {{"entity": "发热", "position": 15}}
  ]
}}
"""
        
        payload = {}
        if api_type.lower() == "deepseek":
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000,
                "stream": False
            }
            
            # 如果API URL不包含完整路径，则使用默认路径
            if not api_url.endswith("/chat/completions"):
                if api_url.endswith("/v1"):
                    api_url = f"{api_url}/chat/completions"
                elif not api_url.endswith("/"):
                    api_url = f"{api_url}/v1/chat/completions"
                else:
                    api_url = f"{api_url}v1/chat/completions"
                    
            print(f"使用DeepSeek API: {api_url}")
                
        elif api_type.lower() == "douban":
            payload = {
                "model": "douban-lite",
                "prompt": prompt,
                "temperature": 0.1,
                "max_tokens": 2000
            }
        else:
            payload = {
                "model": api_type,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
        
        # 发送请求
        print(f"发送API请求到: {api_url}，模型: {api_type}")
        print(f"请求头: {headers}")
        print(f"请求参数: {payload}")
        
        session = _create_unverified_session()
        response = session.post(api_url, headers=headers, json=payload)
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # 提取返回结果中的JSON部分
            if api_type.lower() == "deepseek":
                response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            elif api_type.lower() == "douban":
                response_text = result.get("response", "")
            else:
                response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取JSON部分
            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = re.search(r"{[\s\S]*}", response_text)
                if json_str:
                    json_str = json_str.group(0)
                else:
                    json_str = response_text
            
            # 解析JSON
            try:
                entities = json.loads(json_str)
                
                # 格式化为标准格式
                formatted_entities = {}
                for entity_type, entity_list in entities.items():
                    formatted_entities[entity_type] = []
                    for entity_info in entity_list:
                        # 获取上下文
                        position = entity_info.get("position", 0)
                        entity_text = entity_info.get("entity", "")
                        context_start = max(0, position - 10)
                        context_end = min(len(text), position + len(entity_text) + 10)
                        context = text[context_start:context_end]
                        
                        formatted_entities[entity_type].append({
                            "entity": entity_text,
                            "position": position,
                            "context": context
                        })
                
                return formatted_entities
            except json.JSONDecodeError:
                print(f"解析API返回的JSON失败: {response_text}")
                return {"解析错误": [{"entity": "无法解析API返回的JSON", "position": 0, "context": response_text[:100]}]}
        else:
            print(f"API请求失败: {response.status_code} {response.text}")
            return {"API错误": [{"entity": f"状态码: {response.status_code}", "position": 0, "context": response.text[:100]}]}
    except Exception as e:
        print(f"API实体识别出错: {str(e)}")
        print("尝试使用规则匹配替代")
        return recognize_entities_with_rules(text)

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
    
    config = get_llm_config()
    # 检查是否使用API模式
    if config.get("api_mode", False) and API_AVAILABLE:
        return recognize_entities_with_api(text)
    
    ner_pipeline = load_transformer_model(model_name)
    
    # 如果返回RULE_BASED，使用规则匹配
    if ner_pipeline == "RULE_BASED":
        return recognize_entities_with_rules(text)
    
    # 如果返回API_MODE，使用API识别
    if ner_pipeline == "API_MODE":
        return recognize_entities_with_api(text)
    
    if ner_pipeline is None:
        return {"模型加载失败": [{"entity": "请检查模型配置", "position": 0, "context": "系统无法加载指定的Transformer模型"}]}
    
    custom_entity_types = config["custom_entity_types"]
    chinese_medical_entity_types = config.get("chinese_medical_entity_types", {})
    
    try:
        # 判断文本是否包含中文
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        # 分段处理长文本，避免超出模型最大长度限制
        max_length = 510  # 留出[CLS]和[SEP]的空间
        segments = []
        
        # 如果是中文，按字符级别分割
        if has_chinese:
            # 中文文本按照句子分割，避免实体被截断
            sentences = re.split(r'([。！？；.!?;])', text)
            current_segment = ""
            
            for i in range(0, len(sentences), 2):
                sentence = sentences[i]
                delimiter = sentences[i+1] if i+1 < len(sentences) else ""
                
                if len(current_segment) + len(sentence) + len(delimiter) <= max_length:
                    current_segment += sentence + delimiter
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = sentence + delimiter
            
            if current_segment:
                segments.append(current_segment)
        else:
            # 英文文本按固定长度分割
            segments = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        # 如果没有分段，则处理整个文本
        if not segments:
            segments = [text]
        
        all_entities = []
        offset = 0
        
        for segment in segments:
            if not segment.strip():
                offset += len(segment)
                continue
                
            try:
                # 使用pipeline处理文本
                entities = ner_pipeline(segment)
                # 调整位置偏移
                for entity in entities:
                    entity['start'] += offset
                    entity['end'] += offset
                all_entities.extend(entities)
            except Exception as segment_error:
                print(f"处理文本段落出错: {str(segment_error)}")
                
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
            # 提取实体类型（处理不同模型的标签差异）
            entity_type = None
            if 'entity_group' in entity:
                entity_type = entity['entity_group']
            elif 'entity' in entity:
                # 从B-XXX或I-XXX中提取XXX
                if '-' in entity['entity']:
                    entity_type = entity['entity'].split('-')[-1]
                else:
                    entity_type = entity['entity']
            
            if not entity_type:
                continue
                
            entity_text = text[entity['start']:entity['end']]
            
            # 根据模型类型选择合适的映射
            if "chinese" in model_name.lower() or "med" in model_name.lower():
                mapped_type = chinese_medical_entity_types.get(entity_type, entity_type)
            else:
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
                'score': round(entity['score'], 3) if 'score' in entity else 1.0
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