import edge_tts 
import asyncio 
import os 
 
TEXT = """欢迎来到Python第一周学习。编程的本质，是把你的想法翻译成计算机能听懂的语言。接下来我们会学习环境搭建，和你的第一个Python程序。""" 
VOICE = "zh-CN-XiaoxiaoNeural" 
OUTPUT_AUDIO = "test_user_audio2.mp3" 
OUTPUT_SUBTITLE = "test_user_subtitle2.srt" 
RATE = "+0%" 
VOLUME = "+0%" 
 
async def generate_audio_and_subtitle(): 
    print("📝 测试单次 stream() 调用...")
    print(f"文本长度: {len(TEXT)} 字符")
    
    communicate = edge_tts.Communicate(TEXT, VOICE, rate=RATE, volume=VOLUME) 
    submaker = edge_tts.SubMaker() 
    word_count = 0
    
    print("\n1️⃣ 在单次 stream() 中同时保存音频和捕获 WordBoundary...")
    try:
        with open(OUTPUT_AUDIO, "wb") as f:
            async for chunk in communicate.stream(): 
                if chunk["type"] == "audio": 
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary": 
                    word_count += 1
                    print(f"   📝 识别到词 #{word_count}: '{chunk['text']}'")
                    submaker.feed(chunk["text"], chunk["offset"], chunk["duration"]) 
        
        print(f"\n✅ 音频已生成：{OUTPUT_AUDIO}")
        print(f"✅ 共识别到 {word_count} 个词")
        
        if word_count > 0:
            print("\n2️⃣ 生成 SRT 字幕...")
            srt_content = submaker.get_srt()
            with open(OUTPUT_SUBTITLE, "w", encoding="utf-8") as f: 
                f.write(srt_content) 
            print(f"✅ 字幕已生成：{OUTPUT_SUBTITLE}")
            
            print("\n📄 SRT内容预览:")
            print(srt_content)
        else:
            print("❌ WordBoundary事件未触发！")
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
 
if __name__ == "__main__": 
    if not os.path.exists("test_output"): 
        os.makedirs("test_output") 
    os.chdir("test_output") 
    asyncio.run(generate_audio_and_subtitle())