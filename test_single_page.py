import os
import json
import asyncio
import edge_tts
from mutagen.mp3 import MP3

async def test_single_page():
    """测试单个页面的音频和字幕生成"""
    text = """欢迎来到AI时代的无码架构师课程！这是一门专为文科生设计的AI编程实战课。本周是基础筑基阶段的第一周，我们将学习编程的基本概念和环境搭建。在开始之前，我想告诉你，编程其实没有你想象的那么难，它就像是在指挥一个特别听话但有点笨的机器人。让我们一起开始这段有趣的旅程吧！"""
    
    output_path = "test_audio.mp3"
    timestamps_path = "test_timestamps.json"
    subtitle_path = "test_subtitle.srt"
    
    try:
        communicate = edge_tts.Communicate(text, "zh-CN-YunYangNeural", rate="+0%", volume="+0%")
        
        submaker = edge_tts.SubMaker()
        
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    print(f"📝 识别到词: '{chunk['text']}'")
                    submaker.feed(chunk["text"], chunk["offset"], chunk["duration"])
        
        print(f"✓ 音频生成成功: {output_path}")
        
        audio = MP3(output_path)
        actual_duration = audio.info.length
        print(f"  音频时长: {actual_duration:.2f} 秒")
        
        srt_content = submaker.get_srt()
        print(f"\n📄 SRT字幕内容:\n{srt_content}")
        
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"\n✓ SRT字幕生成成功: {subtitle_path}")
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        print(f"\n📄 分割成 {len(sentences)} 个句子:")
        for i, sent in enumerate(sentences):
            print(f"  {i+1}. {sent}")
        
        caption_timestamps = []
        if submaker.cues:
            print(f"\n📊 SubMaker.cues 内容:")
            for cue in submaker.cues:
                print(f"  {cue}")
            
            sentence_idx = 0
            current_start = 0
            current_text = ""
            
            for cue in submaker.cues:
                if sentence_idx >= len(sentences):
                    break
                
                current_text += cue[2]
                sentence_text = sentences[sentence_idx]
                
                if current_text.endswith(sentence_text) or current_text == sentence_text:
                    caption_timestamps.append({
                        "text": sentence_text,
                        "start": round(current_start / 10000000, 2),
                        "end": round(cue[1] / 10000000, 2)
                    })
                    sentence_idx += 1
                    current_start = cue[1]
                    current_text = ""
        
        if not caption_timestamps and sentences:
            print("\n⚠️ WordBoundary事件未触发，使用备用方案")
            total_chars = sum(len(s) for s in sentences)
            current_time = 0
            for sentence in sentences:
                ratio = len(sentence) / total_chars
                sentence_duration = ratio * actual_duration
                caption_timestamps.append({
                    "text": sentence,
                    "start": round(current_time, 2),
                    "end": round(current_time + sentence_duration, 2)
                })
                current_time += sentence_duration
        
        if caption_timestamps:
            caption_timestamps[-1]['end'] = round(actual_duration, 2)
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON时间戳生成成功: {timestamps_path}")
        
        print("\n📊 时间戳详情:")
        for i, ts in enumerate(caption_timestamps):
            duration = ts["end"] - ts["start"]
            print(f"  {i+1}. [{ts['start']:.2f}s - {ts['end']:.2f}s] ({duration:.2f}s) - {ts['text'][:20]}...")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_page())