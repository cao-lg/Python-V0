import os
import json
import asyncio
import edge_tts
import numpy as np
import soundfile as sf
from silero_vad import load_silero_vad, get_speech_timestamps
import librosa

async def synthesize_and_get_timestamps():
    text = """欢迎来到AI时代的无码架构师课程！这是一门专为文科生设计的AI编程实战课。本周是基础筑基阶段的第一周，我们将学习编程的基本概念和环境搭建。在开始之前，我想告诉你，编程其实没有你想象的那么难，它就像是在指挥一个特别听话但有点笨的机器人。让我们一起开始这段有趣的旅程吧！"""
    
    output_path = "test_silero.wav"
    timestamps_path = "test_silero_timestamps.json"
    subtitle_path = "test_silero_subtitle.srt"
    
    target_sample_rate = 16000
    
    try:
        print("🔊 第一步：使用 Edge-TTS 合成语音...")
        communicate = edge_tts.Communicate(text, "zh-CN-YunYangNeural", rate="+0%", volume="+0%")
        
        wav_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                wav_bytes += chunk["data"]
        
        import io
        audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes))
        
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        if sample_rate != target_sample_rate:
            audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=target_sample_rate)
            sample_rate = target_sample_rate
        
        duration = len(audio_data) / sample_rate
        print(f"✓ 音频生成成功，时长: {duration:.2f} 秒")
        
        sf.write(output_path, audio_data, sample_rate)
        
        print("\n🎙️ 第二步：使用 Silero VAD 检测语音边界...")
        model = load_silero_vad()
        
        speech_timestamps = get_speech_timestamps(audio_data, model, sampling_rate=sample_rate)
        print(f"📊 检测到 {len(speech_timestamps)} 个语音片段")
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        print(f"\n📄 分割成 {len(sentences)} 个句子")
        
        caption_timestamps = align_with_speech_segments(speech_timestamps, sentences, duration, sample_rate)
        
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

def align_with_speech_segments(speech_segments, sentences, total_duration, sample_rate):
    if not speech_segments or not sentences:
        return generate_fallback_timestamps(sentences, total_duration)
    
    segment_times = []
    for seg in speech_segments:
        start = seg['start'] / sample_rate
        end = seg['end'] / sample_rate
        segment_times.append((start, end))
    
    segment_times.sort(key=lambda x: x[0])
    
    merged_segments = []
    for start, end in segment_times:
        if merged_segments and start <= merged_segments[-1][1] + 0.3:
            merged_segments[-1] = (merged_segments[-1][0], max(merged_segments[-1][1], end))
        else:
            merged_segments.append((start, end))
    
    print(f"🔗 合并后: {len(merged_segments)} 个片段")
    for i, (s, e) in enumerate(merged_segments):
        print(f"   片段 {i+1}: [{s:.2f}s - {e:.2f}s]")
    
    result = []
    
    if len(merged_segments) >= len(sentences):
        step = len(merged_segments) / (len(sentences) + 1)
        
        for i in range(len(sentences)):
            idx = int((i + 1) * step)
            if idx >= len(merged_segments):
                idx = len(merged_segments) - 1
            
            if i == 0:
                start = 0.0
            else:
                start = merged_segments[idx][0]
            
            if i == len(sentences) - 1:
                end = total_duration
            else:
                next_idx = idx + 1
                if next_idx < len(merged_segments):
                    end = merged_segments[next_idx][0]
                else:
                    end = merged_segments[idx][1]
            
            result.append({
                "text": sentences[i],
                "start": round(start, 2),
                "end": round(end, 2)
            })
    else:
        for i, (start, end) in enumerate(merged_segments):
            if i == 0:
                start = 0.0
            
            if i < len(sentences):
                result.append({
                    "text": sentences[i],
                    "start": round(start, 2),
                    "end": round(end, 2)
                })
        
        if len(result) < len(sentences):
            remaining = sentences[len(result):]
            last_end = result[-1]["end"] if result else 0
            remaining_duration = total_duration - last_end
            
            for sentence in remaining:
                ratio = len(sentence) / sum(len(s) for s in remaining)
                dur = ratio * remaining_duration
                result.append({
                    "text": sentence,
                    "start": round(last_end, 2),
                    "end": round(last_end + dur, 2)
                })
                last_end += dur
    
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
    asyncio.run(synthesize_and_get_timestamps())