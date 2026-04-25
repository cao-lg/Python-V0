import os
import json
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkalimt.request.v20181012 import SpeechSynthesisRequest
from aliyunsdkalimt.request.v20181012 import GetAsyncJobResultRequest

def create_client(access_key_id, access_key_secret):
    credentials = AccessKeyCredential(access_key_id, access_key_secret)
    client = AcsClient(region_id='cn-shanghai', credential=credentials)
    return client

def synthesize_audio_sync(client, text, voice="Aiyue", format="mp3", sample_rate=16000):
    """同步语音合成"""
    request = SpeechSynthesisRequest.SpeechSynthesisRequest()
    request.set_Text(text)
    request.set_Voice(voice)
    request.set_Format(format)
    request.set_SampleRate(sample_rate)
    request.set_EnableSubtitle(True)
    
    response = client.do_action_with_exception(request)
    
    header_length = int.from_bytes(response[:4], 'big')
    header = json.loads(response[4:4+header_length].decode('utf-8'))
    
    audio_start = 4 + header_length + 4
    audio_length = int.from_bytes(response[4+header_length:audio_start], 'big')
    audio_data = response[audio_start:audio_start+audio_length]
    
    subtitle_start = audio_start + audio_length + 4
    subtitle_length = int.from_bytes(response[audio_start+audio_length:subtitle_start], 'big')
    subtitle_data = response[subtitle_start:subtitle_start+subtitle_length].decode('utf-8')
    
    return audio_data, header, subtitle_data

def parse_subtitle(subtitle_json):
    """解析字幕数据"""
    try:
        subtitle = json.loads(subtitle_json)
        timestamps = []
        for item in subtitle.get('Subtitles', []):
            timestamps.append({
                "text": item.get('Text', ''),
                "start": round(item.get('BeginTime', 0) / 1000, 2),
                "end": round(item.get('EndTime', 0) / 1000, 2)
            })
        return timestamps
    except:
        return []

def process_page(text, output_path, timestamps_path, client):
    """处理单个页面的语音合成"""
    print(f"🔊 正在合成语音...")
    
    try:
        audio_data, header, subtitle_data = synthesize_audio_sync(client, text)
        
        with open(output_path, "wb") as f:
            f.write(audio_data)
        print(f"✓ 音频生成成功: {output_path}")
        
        timestamps = parse_subtitle(subtitle_data)
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        if timestamps and sentences:
            merged_timestamps = merge_to_sentences(timestamps, sentences)
        else:
            merged_timestamps = generate_fallback_timestamps(text)
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(merged_timestamps, f, ensure_ascii=False, indent=2)
        print(f"✓ 时间戳生成成功: {timestamps_path}")
        
        return True
    except Exception as e:
        print(f"✗ 生成失败: {str(e)}")
        return False

def merge_to_sentences(word_timestamps, sentences):
    """将词级时间戳合并为句子级"""
    merged = []
    sent_idx = 0
    current_start = 0
    current_text = ""
    
    for word in word_timestamps:
        if sent_idx >= len(sentences):
            break
        
        current_text += word["text"]
        sentence = sentences[sent_idx]
        
        if current_text.endswith(sentence) or len(current_text) >= len(sentence):
            merged.append({
                "text": sentence,
                "start": word_timestamps[0]["start"] if merged else word["start"],
                "end": word["end"]
            })
            sent_idx += 1
            current_text = ""
    
    return merged

def generate_fallback_timestamps(text):
    """备用方案：根据文本长度估算时间戳"""
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    if not sentences:
        return []
    
    avg_duration = len(text) * 0.08
    total_chars = sum(len(s) for s in sentences)
    
    timestamps = []
    current_time = 0
    for sentence in sentences:
        ratio = len(sentence) / total_chars
        duration = ratio * avg_duration
        timestamps.append({
            "text": sentence,
            "start": round(current_time, 2),
            "end": round(current_time + duration, 2)
        })
        current_time += duration
    
    if timestamps:
        timestamps[-1]["end"] = round(avg_duration, 2)
    
    return timestamps

def process_week(week_num, client):
    json_path = f"data/week{week_num}.json"
    audio_dir = f"audio/week{week_num}"
    
    if not os.path.exists(json_path):
        print(f"⚠️ 未找到文件: {json_path}")
        return
    
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"\n📚 处理第{week_num}周: {data['title']}")
    
    for page in data["pages"]:
        page_id = page["id"]
        speech_text = page.get("speech", "")
        
        if not speech_text:
            print(f"跳过页面 {page_id} (无语音内容)")
            continue
        
        audio_path = f"{audio_dir}/page{page_id}.mp3"
        timestamps_path = f"{audio_dir}/page{page_id}_timestamps.json"
        
        print(f"\n📄 页面 {page_id}")
        process_page(speech_text, audio_path, timestamps_path, client)

def main():
    print("🎙️ 通义语音合成脚本")
    print("=" * 50)
    
    access_key_id = input("请输入阿里云Access Key ID: ").strip()
    access_key_secret = input("请输入阿里云Access Key Secret: ").strip()
    
    if not access_key_id or not access_key_secret:
        print("❌ 请提供有效的阿里云凭证")
        return
    
    try:
        client = create_client(access_key_id, access_key_secret)
    except Exception as e:
        print(f"❌ 创建客户端失败: {str(e)}")
        return
    
    os.makedirs("audio", exist_ok=True)
    
    for week_num in range(1, 4):
        process_week(week_num, client)
    
    print("\n🎉 所有语音合成完成！")

if __name__ == "__main__":
    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.auth.credentials import AccessKeyCredential
        from aliyunsdkalimt.request.v20181012 import SpeechSynthesisRequest
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖: pip install aliyun-python-sdk-alimt")
        exit(1)
    
    main()