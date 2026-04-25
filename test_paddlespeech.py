import os
import json
import subprocess
import wave

def test_paddlespeech_cli():
    text = """欢迎来到AI时代的无码架构师课程！这是一门专为文科生设计的AI编程实战课。本周是基础筑基阶段的第一周，我们将学习编程的基本概念和环境搭建。"""
    
    output_path = "test_paddle_cli.wav"
    timestamps_path = "test_paddle_cli_timestamps.json"
    
    try:
        print("🔊 正在使用 PaddleSpeech CLI 合成语音...")
        
        input_file = "tts_input.txt"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        cmd = [
            "paddlespeech", "tts",
            "--input", input_file,
            "--output", output_path,
            "--am", "fastspeech2_aishell3",
            "--voc", "pwgan_aishell3",
            "--lang", "zh"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✓ 音频生成成功: {output_path}")
            
            with wave.open(output_path, 'rb') as wf:
                sample_rate = wf.getframerate()
                n_frames = wf.getnframes()
                duration = n_frames / sample_rate
                print(f"🎵 采样率: {sample_rate}, 音频长度: {duration:.2f} 秒")
            
            sentences = [s.strip() for s in text.split('。') if s.strip()]
            caption_timestamps = []
            
            if sentences:
                total_chars = sum(len(s) for s in sentences)
                current_time = 0
                
                for sentence in sentences:
                    ratio = len(sentence) / total_chars
                    sentence_duration = ratio * duration
                    caption_timestamps.append({
                        "text": sentence,
                        "start": round(current_time, 2),
                        "end": round(current_time + sentence_duration, 2)
                    })
                    current_time += sentence_duration
            
            with open(timestamps_path, "w", encoding="utf-8") as f:
                json.dump(caption_timestamps, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 时间戳生成成功: {timestamps_path}")
            
            print("\n📊 句子时间戳详情:")
            for i, ts in enumerate(caption_timestamps):
                dur = ts["end"] - ts["start"]
                print(f"  {i+1}. [{ts['start']:.2f}s - {ts['end']:.2f}s] ({dur:.2f}s) - {ts['text'][:30]}...")
            
            print("\n✅ PaddleSpeech CLI 测试完成！")
        else:
            print(f"\n❌ 命令执行失败")
            print(f"错误信息: {result.stderr}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paddlespeech_cli()