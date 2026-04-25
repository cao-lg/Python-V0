import os
import json
import asyncio
import edge_tts
from mutagen.mp3 import MP3

async def synthesize_audio(text, voice, output_path, timestamps_path):
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+0%", volume="+0%")
        
        boundaries = []
        
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    boundaries.append(chunk["offset"])
        
        audio = MP3(output_path)
        actual_duration = audio.info.length
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        
        if sentences:
            caption_timestamps = generate_timestamps_with_boundaries(sentences, boundaries, actual_duration)
        else:
            caption_timestamps = []
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"✗ 生成失败 {output_path}: {str(e)}")
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        if sentences:
            try:
                audio = MP3(output_path)
                actual_duration = audio.info.length
            except:
                actual_duration = len(text) * 0.08
            
            caption_timestamps = generate_fallback_timestamps(sentences, actual_duration)
            
            with open(timestamps_path, "w", encoding="utf-8") as f:
                json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
        
        return False

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
        speech_text = page.get("speech", "")
        
        if not speech_text:
            print(f"跳过页面 {page_id} (无语音内容)")
            continue
        
        audio_path = f"{audio_dir}/page{page_id}.mp3"
        timestamps_path = f"{audio_dir}/page{page_id}_timestamps.json"
        
        print(f"🔊 页面 {page_id}...", end=" ")
        success = await synthesize_audio(speech_text, "zh-CN-YunYangNeural", audio_path, timestamps_path)
        print("✓" if success else "✗")

async def main():
    print("🎙️ Edge-TTS 语音合成脚本")
    print("=" * 50)
    print("💡 使用微软免费TTS服务")
    print()
    
    os.makedirs("audio", exist_ok=True)
    
    for week_num in range(1, 4):
        await process_week(week_num)
    
    print("\n🎉 所有语音合成完成！")

if __name__ == "__main__":
    try:
        import edge_tts
        from mutagen.mp3 import MP3
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖: pip install edge-tts mutagen")
        exit(1)
    
    asyncio.run(main())