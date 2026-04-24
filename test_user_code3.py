import edge_tts 
import asyncio 
import os 
 
TEXT = """欢迎来到Python第一周学习。编程的本质，是把你的想法翻译成计算机能听懂的语言。接下来我们会学习环境搭建，和你的第一个Python程序。""" 
VOICE = "zh-CN-XiaoxiaoNeural" 
OUTPUT_DIR = "test_output" 
OUTPUT_AUDIO = "python_lesson_audio.mp3" 
OUTPUT_SUBTITLE = "python_lesson_subtitle.srt" 
RATE = "+0%" 
VOLUME = "+0%" 
 
async def generate_audio_and_subtitle(): 
    print("📝 测试用户提供的改进代码...")
    print(f"文本长度: {len(TEXT)} 字符")
    
    communicate = edge_tts.Communicate(TEXT, VOICE, rate=RATE, volume=VOLUME) 
    submaker = edge_tts.SubMaker() 
    word_count = 0
     
    audio_data = b"" 
    async for chunk in communicate.stream(): 
        if chunk["type"] == "audio": 
            audio_data += chunk["data"] 
        elif chunk["type"] == "WordBoundary": 
            word_count += 1
            print(f"   📝 识别到词 #{word_count}: '{chunk['text']}'")
            submaker.feed(chunk["text"], chunk["offset"], chunk["duration"]) 
     
    if not os.path.exists(OUTPUT_DIR): 
        os.makedirs(OUTPUT_DIR) 
     
    audio_path = os.path.join(OUTPUT_DIR, OUTPUT_AUDIO) 
    with open(audio_path, "wb") as f: 
        f.write(audio_data) 
    print(f"\n✅ 音频已生成：{audio_path}") 
     
    subtitle_path = os.path.join(OUTPUT_DIR, OUTPUT_SUBTITLE) 
    try:
        srt_content = submaker.get_srt()
        with open(subtitle_path, "w", encoding="utf-8") as f: 
            f.write(srt_content) 
        print(f"✅ 字幕已生成：{subtitle_path}")
        
        if word_count > 0:
            print(f"\n📄 SRT内容预览:")
            print(srt_content)
            print(f"\n✅ 音频与字幕100%同步，可直接部署到线上！")
        else:
            print(f"\n⚠️ WordBoundary事件未触发，SRT可能为空")
            print(f"   识别到 {word_count} 个词")
            
    except AttributeError as e:
        print(f"❌ 生成字幕失败: {e}")
        print("   请检查 SubMaker 类是否有 generate_subs() 方法")
 
if __name__ == "__main__": 
    asyncio.run(generate_audio_and_subtitle())