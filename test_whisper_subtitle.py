import os
import json
import asyncio
import edge_tts
import whisper
from mutagen.mp3 import MP3

async def synthesize_and_transcribe():
    text = """欢迎来到AI时代的无码架构师课程！这是一门专为文科生设计的AI编程实战课。本周是基础筑基阶段的第一周，我们将学习编程的基本概念和环境搭建。在开始之前，我想告诉你，编程其实没有你想象的那么难，它就像是在指挥一个特别听话但有点笨的机器人。让我们一起开始这段有趣的旅程吧！"""
    
    output_path = "test_whisper.mp3"
    timestamps_path = "test_whisper_timestamps.json"
    subtitle_path = "test_whisper_subtitle.srt"
    
    try:
        print("🔊 第一步：使用 Edge-TTS 合成语音...")
        communicate = edge_tts.Communicate(text, "zh-CN-YunYangNeural", rate="+0%", volume="+0%")
        
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        audio = MP3(output_path)
        duration = audio.info.length
        print(f"✓ 音频生成成功，时长: {duration:.2f} 秒")
        
        print("\n🎙️ 第二步：使用 Whisper tiny 模型进行语音识别...")
        model = whisper.load_model("tiny")
        result = model.transcribe(output_path, word_timestamps=True, language="zh")
        
        print(f"\n📊 Whisper 识别结果:")
        print(f"  原始文本: {text[:50]}...")
        print(f"  识别文本: {result['text'][:50]}...")
        
        caption_timestamps = []
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        
        if result.get('segments'):
            caption_timestamps = align_with_sentences(result['segments'], sentences, duration)
        else:
            caption_timestamps = generate_fallback_timestamps(sentences, duration)
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON时间戳生成成功: {timestamps_path}")
        
        generate_srt(caption_timestamps, subtitle_path)
        print(f"✓ SRT字幕生成成功: {subtitle_path}")
        
        print("\n📊 最终时间戳详情:")
        for i, ts in enumerate(caption_timestamps):
            dur = ts["end"] - ts["start"]
            print(f"  {i+1}. [{ts['start']:.2f}s - {ts['end']:.2f}s] ({dur:.2f}s) - {ts['text'][:30]}...")
        
        print("\n✅ 完成！")
        
    except Exception as e:
        print(f"\n❌ 失败: {str(e)}")
        import traceback
        traceback.print_exc()

def align_with_sentences(segments, sentences, total_duration):
    result = []
    segment_idx = 0
    sent_idx = 0
    
    while sent_idx < len(sentences) and segment_idx < len(segments):
        current_sentence = sentences[sent_idx]
        current_segment = segments[segment_idx]
        segment_text = current_segment['text'].strip()
        
        if segment_text == "" or segment_text.isspace():
            segment_idx += 1
            continue
        
        combined_text = ""
        start_time = current_segment['start']
        end_time = current_segment['end']
        temp_idx = segment_idx
        
        while temp_idx < len(segments):
            seg_text = segments[temp_idx]['text'].strip()
            if seg_text:
                combined_text += seg_text
            
            end_time = segments[temp_idx]['end']
            
            if combined_text and (current_sentence.startswith(combined_text) or combined_text.startswith(current_sentence[:len(combined_text)])):
                if len(combined_text) >= len(current_sentence) * 0.8:
                    break
            temp_idx += 1
        
        if combined_text:
            result.append({
                "text": current_sentence,
                "start": round(start_time, 2),
                "end": round(end_time, 2)
            })
            segment_idx = temp_idx
            sent_idx += 1
        else:
            segment_idx += 1
    
    if sent_idx < len(sentences):
        remaining = sentences[sent_idx:]
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
    asyncio.run(synthesize_and_transcribe())