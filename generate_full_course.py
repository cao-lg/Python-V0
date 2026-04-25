import os
import json
import asyncio
import edge_tts
import numpy as np
import soundfile as sf
from silero_vad import load_silero_vad, get_speech_timestamps
import librosa

TARGET_SAMPLE_RATE = 16000

async def synthesize_audio_with_timestamps(text, voice, output_path):
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+0%", volume="+0%")
        
        wav_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                wav_bytes += chunk["data"]
        
        import io
        audio_data, sample_rate = sf.read(io.BytesIO(wav_bytes))
        
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        if sample_rate != TARGET_SAMPLE_RATE:
            audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=TARGET_SAMPLE_RATE)
            sample_rate = TARGET_SAMPLE_RATE
        
        duration = len(audio_data) / sample_rate
        sf.write(output_path, audio_data, sample_rate)
        
        model = load_silero_vad()
        speech_timestamps = get_speech_timestamps(audio_data, model, sampling_rate=sample_rate)
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        
        if sentences:
            caption_timestamps = align_with_speech_segments(speech_timestamps, sentences, duration, sample_rate)
        else:
            caption_timestamps = []
        
        return caption_timestamps, duration
    except Exception as e:
        print(f"❌ 合成失败: {str(e)}")
        return [], 0.0

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

def update_json_with_timestamps(json_path, audio_dir):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total_duration = 0.0
    
    for page in data["pages"]:
        page_id = page["id"]
        timestamps_file = f"{audio_dir}/page{page_id}_timestamps.json"
        
        if os.path.exists(timestamps_file):
            with open(timestamps_file, "r", encoding="utf-8") as f:
                timestamps = json.load(f)
            page["timestamps"] = timestamps
            
            if timestamps:
                page_duration = timestamps[-1]["end"]
                page["duration"] = page_duration
                total_duration += page_duration
    
    data["totalDuration"] = round(total_duration, 2)
    
    output_path = json_path.replace(".json", "_with_timestamps.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_path

async def process_week(week_num):
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
        page_title = page["title"]
        speech_text = page.get("speech", "")
        
        if not speech_text:
            print(f"⏭️ 跳过页面 {page_id} (无语音内容)")
            continue
        
        audio_path = f"{audio_dir}/page{page_id}.wav"
        timestamps_path = f"{audio_dir}/page{page_id}_timestamps.json"
        
        print(f"\n🔊 页面 {page_id}: {page_title}")
        caption_timestamps, duration = await synthesize_audio_with_timestamps(
            speech_text, "zh-CN-YunYangNeural", audio_path
        )
        
        if caption_timestamps:
            with open(timestamps_path, "w", encoding="utf-8") as f:
                json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 音频生成成功: page{page_id}.wav ({duration:.2f}s)")
            print(f"✓ 时间戳生成: {len(caption_timestamps)} 条")
        else:
            print(f"✗ 生成失败")
    
    updated_json = update_json_with_timestamps(json_path, audio_dir)
    print(f"\n📝 更新后的JSON: {updated_json}")

async def main():
    print("🎙️ Edge-TTS + Silero VAD 完整课程生成")
    print("=" * 50)
    print("💡 生成音频、字幕时间戳，并更新课程JSON")
    print()
    
    os.makedirs("audio", exist_ok=True)
    
    for week_num in range(1, 4):
        await process_week(week_num)
    
    print("\n🎉 所有课程生成完成！")

if __name__ == "__main__":
    try:
        import edge_tts
        import librosa
        import soundfile as sf
        from silero_vad import load_silero_vad, get_speech_timestamps
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖: pip install edge-tts librosa soundfile silero-vad")
        exit(1)
    
    asyncio.run(main())