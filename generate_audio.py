import os
import json
import asyncio
import edge_tts
from mutagen.mp3 import MP3
import whisper

async def synthesize_audio(text, voice, output_path, timestamps_path):
    """合成语音并使用Whisper生成精准时间戳"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+0%", volume="+0%")
        
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        print(f"✓ 生成成功: {output_path}")
        
        audio = MP3(output_path)
        actual_duration = audio.info.length
        print(f"  实际时长: {actual_duration:.2f} 秒")
        
        model = whisper.load_model("tiny")
        result = model.transcribe(output_path, word_timestamps=True)
        
        sentences = [s.strip() for s in text.split('。') if s.strip()]
        print(f"  分割成 {len(sentences)} 个句子")
        
        whisper_segments = result.get('segments', [])
        caption_timestamps = []
        
        if whisper_segments:
            whisper_total_duration = whisper_segments[-1]['end']
            scale_factor = actual_duration / whisper_total_duration
            
            total_sentences = len(sentences)
            total_segments = len(whisper_segments)
            
            if total_segments >= total_sentences:
                segments_per_sentence = total_segments // total_sentences
                remainder = total_segments % total_sentences
                
                segment_idx = 0
                for i in range(total_sentences):
                    segments_used = segments_per_sentence + (1 if i < remainder else 0)
                    
                    start_time = whisper_segments[segment_idx]['start'] * scale_factor
                    end_idx = min(segment_idx + segments_used, total_segments)
                    end_time = whisper_segments[end_idx - 1]['end'] * scale_factor
                    
                    caption_timestamps.append({
                        "text": sentences[i],
                        "start": round(start_time, 2),
                        "end": round(end_time, 2)
                    })
                    
                    segment_idx = end_idx
            else:
                sentences_per_segment = (total_sentences + total_segments - 1) // total_segments
                
                sentence_idx = 0
                for segment in whisper_segments:
                    if sentence_idx >= total_sentences:
                        break
                    
                    end_idx = min(sentence_idx + sentences_per_segment, total_sentences)
                    merged_text = '。'.join(sentences[sentence_idx:end_idx])
                    
                    caption_timestamps.append({
                        "text": merged_text,
                        "start": round(segment['start'] * scale_factor, 2),
                        "end": round(segment['end'] * scale_factor, 2)
                    })
                    
                    sentence_idx = end_idx
            
            if caption_timestamps:
                caption_timestamps[-1]['end'] = round(actual_duration, 2)
        else:
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
        
        print(f"  生成 {len(caption_timestamps)} 条时间戳")
        
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
        print(f"✓ 生成时间戳: {timestamps_path}")
        
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
            
            total_chars = sum(len(s) for s in sentences)
            caption_timestamps = []
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
            
            with open(timestamps_path, "w", encoding="utf-8") as f:
                json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
            print(f"✓ 使用备用方案生成时间戳")
        
        return False

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
        
        print(f"🔊 正在生成: page{page_id}...")
        await synthesize_audio(speech_text, "zh-CN-YunYangNeural", audio_path, timestamps_path)

async def main():
    print("🎙️ Edge-TTS 语音合成脚本（使用Whisper时间戳）")
    print("=" * 50)
    
    os.makedirs("audio", exist_ok=True)
    
    for week_num in range(1, 4):
        await process_week(week_num)
    
    print("\n🎉 所有语音合成完成！")

if __name__ == "__main__":
    try:
        import edge_tts
        from mutagen.mp3 import MP3
        import whisper
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖: pip install edge-tts mutagen openai-whisper")
        exit(1)
    
    asyncio.run(main())