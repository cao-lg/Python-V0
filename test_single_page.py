import os
import json
import asyncio
import edge_tts
from mutagen.mp3 import MP3

async def test_single_page():
    text = """欢迎来到AI时代的无码架构师课程！这是一门专为文科生设计的AI编程实战课。本周是基础筑基阶段的第一周，我们将学习编程的基本概念和环境搭建。在开始之前，我想告诉你，编程其实没有你想象的那么难，它就像是在指挥一个特别听话但有点笨的机器人。让我们一起开始这段有趣的旅程吧！"""
    
    output_path = "test_audio.mp3"
    timestamps_path = "test_timestamps.json"
    subtitle_path = "test_subtitle.srt"
    
    try:
        communicate = edge_tts.Communicate(text, "zh-CN-YunYangNeural", rate="+0%", volume="+0%")
        
        print("🔊 正在合成语音...")
        
        boundaries = []
        
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    boundaries.append(chunk["offset"])
        
        audio = MP3(output_path)
        actual_duration = audio.info.length
        print(f"\n✓ 音频生成成功: {output_path}")
        print(f"  音频时长: {actual_duration:.2f} 秒")
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        print(f"\n📄 分割成 {len(sentences)} 个句子")
        
        caption_timestamps = generate_timestamps_with_boundaries(sentences, boundaries, actual_duration)
        
        print("\n📊 生成的时间戳:")
        for i, ts in enumerate(caption_timestamps):
            duration = ts["end"] - ts["start"]
            print(f"  {i+1}. [{ts['start']:.2f}s - {ts['end']:.2f}s] ({duration:.2f}s) - {ts['text'][:30]}...")
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON时间戳生成成功: {timestamps_path}")
        
        generate_srt(caption_timestamps, subtitle_path)
        print(f"✓ SRT字幕生成成功: {subtitle_path}")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def generate_timestamps_with_boundaries(sentences, boundaries, total_duration):
    valid_boundaries = sorted([b for b in boundaries if 0 < b < total_duration * 10000000])
    
    if not valid_boundaries:
        return generate_fallback_timestamps(sentences, total_duration)
    
    result = []
    sentence_count = len(sentences)
    boundary_count = len(valid_boundaries)
    
    if boundary_count >= sentence_count:
        selected_indices = []
        for i in range(sentence_count):
            idx = int((i + 1) * boundary_count / (sentence_count + 1))
            if idx < boundary_count:
                selected_indices.append(idx)
        
        selected = [valid_boundaries[i] for i in selected_indices]
    else:
        selected = valid_boundaries
    
    selected = [0] + selected + [total_duration * 10000000]
    
    for i in range(min(len(sentences), len(selected) - 1)):
        start = round(selected[i] / 10000000, 2)
        end = round(selected[i+1] / 10000000, 2)
        
        if i > 0 and start < result[i-1]["end"]:
            start = result[i-1]["end"]
        
        result.append({
            "text": sentences[i],
            "start": start,
            "end": min(end, total_duration)
        })
    
    if len(result) < len(sentences):
        remaining = sentences[len(result):]
        last_end = result[-1]["end"] if result else 0
        remaining_duration = total_duration - last_end
        
        for sentence in remaining:
            ratio = len(sentence) / sum(len(s) for s in remaining)
            duration = ratio * remaining_duration
            result.append({
                "text": sentence,
                "start": round(last_end, 2),
                "end": round(last_end + duration, 2)
            })
            last_end += duration
    
    if result:
        result[-1]["end"] = round(total_duration, 2)
    
    return result

def generate_fallback_timestamps(sentences, duration):
    if not sentences:
        return []
    
    total_chars = sum(len(s) for s in sentences)
    timestamps = []
    current_time = 0
    
    for sentence in sentences:
        ratio = len(sentence) / total_chars
        sentence_duration = ratio * duration
        timestamps.append({
            "text": sentence,
            "start": round(current_time, 2),
            "end": round(current_time + sentence_duration, 2)
        })
        current_time += sentence_duration
    
    return timestamps

def generate_srt(timestamps, output_path):
    srt_lines = []
    for i, ts in enumerate(timestamps):
        start = format_time(ts["start"])
        end = format_time(ts["end"])
        srt_lines.append(str(i+1))
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(ts["text"])
        srt_lines.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

if __name__ == "__main__":
    asyncio.run(test_single_page())