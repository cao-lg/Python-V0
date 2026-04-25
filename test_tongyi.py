import os
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkalimt.request.v20181012 import SpeechSynthesisRequest

def test_tongyi_tts():
    text = """欢迎来到AI时代的无码架构师课程！这是一门专为文科生设计的AI编程实战课。本周是基础筑基阶段的第一周，我们将学习编程的基本概念和环境搭建。在开始之前，我想告诉你，编程其实没有你想象的那么难，它就像是在指挥一个特别听话但有点笨的机器人。让我们一起开始这段有趣的旅程吧！"""
    
    access_key_id = input("请输入阿里云Access Key ID: ").strip()
    access_key_secret = input("请输入阿里云Access Key Secret: ").strip()
    
    if not access_key_id or not access_key_secret:
        print("❌ 请提供有效的阿里云凭证")
        return
    
    try:
        credentials = AccessKeyCredential(access_key_id, access_key_secret)
        client = AcsClient(region_id='cn-shanghai', credential=credentials)
        
        request = SpeechSynthesisRequest.SpeechSynthesisRequest()
        request.set_Text(text)
        request.set_Voice("Aiyue")
        request.set_Format("mp3")
        request.set_SampleRate(16000)
        request.set_EnableSubtitle(True)
        
        print("🔊 正在合成语音...")
        response = client.do_action_with_exception(request)
        
        header_length = int.from_bytes(response[:4], 'big')
        header = json.loads(response[4:4+header_length].decode('utf-8'))
        
        audio_start = 4 + header_length + 4
        audio_length = int.from_bytes(response[4+header_length:audio_start], 'big')
        audio_data = response[audio_start:audio_start+audio_length]
        
        subtitle_start = audio_start + audio_length + 4
        subtitle_length = int.from_bytes(response[audio_start+audio_length:subtitle_start], 'big')
        subtitle_data = response[subtitle_start:subtitle_start+subtitle_length].decode('utf-8')
        
        with open("test_tongyi.mp3", "wb") as f:
            f.write(audio_data)
        print("✓ 音频文件已保存: test_tongyi.mp3")
        
        subtitle = json.loads(subtitle_data)
        print(f"\n📊 字幕数据:")
        print(f"  词数: {len(subtitle.get('Subtitles', []))}")
        print(f"\n📝 词级时间戳:")
        
        for i, item in enumerate(subtitle.get('Subtitles', [])):
            print(f"  {i+1}. [{item['BeginTime']/1000:.2f}s - {item['EndTime']/1000:.2f}s] {item['Text']}")
        
        timestamps_path = "test_tongyi_timestamps.json"
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        word_timestamps = subtitle.get('Subtitles', [])
        
        merged_timestamps = []
        sent_idx = 0
        current_start = 0
        
        for word in word_timestamps:
            if sent_idx >= len(sentences):
                break
            
            sentence = sentences[sent_idx]
            if word['Text'] and sentence.startswith(word['Text']):
                current_start = word['BeginTime']
                remaining = sentence[len(word['Text']):]
                
                next_idx = word_timestamps.index(word) + 1
                while remaining and next_idx < len(word_timestamps):
                    next_word = word_timestamps[next_idx]
                    if remaining.startswith(next_word['Text']):
                        remaining = remaining[len(next_word['Text']):]
                        next_idx += 1
                    else:
                        break
                
                merged_timestamps.append({
                    "text": sentence,
                    "start": round(current_start / 1000, 2),
                    "end": round(word_timestamps[next_idx-1]['EndTime'] / 1000, 2)
                })
                sent_idx += 1
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(merged_timestamps, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 句子级时间戳已保存: {timestamps_path}")
        
        print(f"\n📊 句子时间戳详情:")
        for i, ts in enumerate(merged_timestamps):
            duration = ts["end"] - ts["start"]
            print(f"  {i+1}. [{ts['start']:.2f}s - {ts['end']:.2f}s] ({duration:.2f}s) - {ts['text'][:20]}...")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tongyi_tts()