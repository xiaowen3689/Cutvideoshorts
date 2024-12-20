from moviepy.editor import *
import os
import random
import time
import math

def calculate_possible_combinations(n, r=8):
    """计算可能的组合数"""
    try:
        return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))
    except ValueError:
        return 0

def create_frame_processor(clip, w, h):
    """创建帧处理器"""
    def process_frame(t):
        # 2秒内从1.0变到1.2，使用线性缩放
        scale = 1 + (0.2 * t)  # 移除了 /2，让缩放更明显
        scaled_w = int(w * scale)
        scaled_h = int(h * scale)
        
        # 创建放大的帧
        frame = clip.get_frame(t)
        resized = resize_frame(frame, (scaled_w, scaled_h))
        
        # 裁剪到原始尺寸（保持居中）
        x = (scaled_w - w) // 2
        y = (scaled_h - h) // 2
        cropped = resized[y:y+h, x:x+w]
        
        return cropped
    return process_frame

def create_video_with_zoom(image_folder, audio_path, output_folder, selected_files):
    """创建单个视频"""
    print(f"\n选择的图片文件：")
    for i, file in enumerate(selected_files, 1):
        print(f"{i}. {file}")
    
    # 确保出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    print("开始处理图片...")
    
    # 创建图片剪辑列表
    clips = []
    for i, img_file in enumerate(selected_files, 1):
        img_path = os.path.join(image_folder, img_file)
        print(f"处理第 {i}/8 张图片: {img_file}")
        
        # 创建图片剪辑并设置持续时间
        base_clip = ImageClip(img_path).set_duration(2)
        w, h = base_clip.size
        
        # 创建帧处理器
        frame_processor = create_frame_processor(base_clip, w, h)
        
        # 建新的视频剪辑
        zoomed_clip = VideoClip(frame_processor, duration=2).set_fps(24)
        clips.append(zoomed_clip)
        print(f"已添加第 {i} 个片段")
    
    print(f"总共创建了 {len(clips)} 个片段")
    print("正在合并视频片段...")
    final_clip = concatenate_videoclips(clips, method="compose")
    print(f"合并后的视频长度: {final_clip.duration} 秒")
    
    print("添加音频...")
    audio = AudioFileClip(audio_path)
    audio = audio.subclip(0, final_clip.duration)
    final_clip = final_clip.set_audio(audio)
    
    # 生成输出文件名
    timestamp = int(time.time())
    output_path = os.path.join(output_folder, f'output_video_{timestamp}.mp4')
    print(f"\n正在生成视频文件: {output_path}")
    
    # 写入视频文件
    final_clip.write_videofile(output_path, 
                             fps=24, 
                             codec='libx264',
                             audio_codec='aac',
                             verbose=False)
    
    print("清理资源...")
    final_clip.close()
    audio.close()
    for clip in clips:
        clip.close()
    
    print(f"视频生成完成: {output_path}")
    return output_path

def resize_frame(frame, size):
    """调整帧大小的辅助函数"""
    from PIL import Image
    import numpy as np
    img = Image.fromarray(frame)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return np.array(img)

def create_multiple_videos(image_folder, audio_path, output_folder, min_videos=10):
    """创建多个视频，确保图片组合不重复"""
    # 获取所有图片文件
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # 计算可能的组合数
    total_images = len(image_files)
    possible_combinations = calculate_possible_combinations(total_images)
    
    if total_images < 8:
        raise ValueError(f"文件夹中只有{total_images}张图片，至少需要8张图片才能生成视频")
    
    # 确定要生成的视频数量
    videos_to_create = min(min_videos, possible_combinations)
    print(f"\n将生成 {videos_to_create} 个视频...")
    
    # 用于记录已使用的组合
    used_combinations = set()
    created_videos = []
    
    while len(created_videos) < videos_to_create:
        try:
            # 随机选择8张图片
            selected_files = tuple(sorted(random.sample(image_files, 8)))
            
            # 检查是否是重复组合
            if selected_files in used_combinations:
                continue
                
            print(f"\n正在生成第 {len(created_videos) + 1}/{videos_to_create} 个视频...")
            
            output_path = create_video_with_zoom(
                image_folder, 
                audio_path, 
                output_folder, 
                selected_files
            )
            
            created_videos.append(output_path)
            used_combinations.add(selected_files)
            print(f"视频已生成: {output_path}")
            
        except Exception as e:
            print(f"生成视频时出错: {str(e)}")
            import traceback
            print("详细错误信息:")
            print(traceback.format_exc())
            break
    
    return created_videos

# 使用示例
if __name__ == "__main__":
    image_folder = r"D:\sailing\Youtube Shorts\演示图"
    audio_path = r"D:\sailing\Youtube Shorts\演示图\biubiubiu.m4a"
    output_folder = r"D:\sailing\Youtube Shorts\生成视频"
    
    try:
        # 首先检查文件夹和文件是否存在
        if not os.path.exists(image_folder):
            raise ValueError(f"图片文件夹不存在: {image_folder}")
        if not os.path.exists(audio_path):
            raise ValueError(f"音频文件不存在: {audio_path}")
            
        # 检查图片文件夹中是否有图片
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        print(f"找到 {len(image_files)} 张图片")
        
        created_videos = create_multiple_videos(image_folder, audio_path, output_folder)
        if created_videos:
            print(f"\n成功生成 {len(created_videos)} 个视频")
            print("视频保存在以下路径：")
            for video in created_videos:
                print(video)
    except Exception as e:
        import traceback
        print(f"生成视频时出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc()) 