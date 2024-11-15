import streamlit as st
import os
import time
from datetime import datetime
import subprocess
import random

# 设置页面标题
st.title("图片上传页面")

if not os.path.exists("data"):
    os.makedirs("data")

# 用于存储上传的图片文件
uploaded_files = st.file_uploader("请上传多个图片文件", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

vf_list = [
    "zoompan='1.5':x='if(lte(on,-1),(iw-iw/zoom)/2,x+3)':y='if(lte(on,1),(ih-ih/zoom)/2,y)':d=150",
    "zoompan='1.5':x='if(lte(on,1),(iw/zoom)/2,x-3)':y='if(lte(on,1),(ih-ih/zoom)/2,y)':d=150",
    "zoompan='1.5':x='if(lte(on,1),(iw-iw/zoom)/2,x)':y='if(lte(on,-1),(ih-ih/zoom)/2,y+2)':d=150",
    "zoompan='1.5':x='if(lte(on,1),(iw-iw/zoom)/2,x)':y='if(lte(on,1),(ih/zoom)/2,y-2)':d=150",
    "scale=1920x1080,zoompan='1.2':x='if(lte(on,-1),(iw-iw/zoom)/2,x+2)':y='if(lte(on,-1),(ih-ih/zoom)/2,y+1)':d=50:s=1920x1080",
    "scale=1920x1080,zoompan='1.2':x='if(lte(on,1),(iw/zoom)/2,x-3)':y='if(lte(on,1),(ih-ih/zoom)/2,y-2)':d=50:s=1920x1080"
]


def gen_video_by_img(img_path, video_path, fade_path):
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-loop', '1',
        '-i', img_path,
        '-c:v', 'libx264',
        '-t', str(1),
        '-vf', random.choice(vf_list),
        video_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"图片已成功转换为视频，保存至 {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"转换过程中出现错误：{e}")
        
        return
    
    fade_command = [
        'ffmpeg',
        '-y',
        '-i', video_path,
        '-vf', "fade=t=in:st=0:d=0.3,fade=t=out:st=0.7:d=0.2",
        fade_path
    ]
    try:
        subprocess.run(fade_command, check=True)
        print(f"视频fade效果增加成功，保存至 {fade_path}")
    except subprocess.CalledProcessError as e:
        print(f"视频fade效果增加过程中出现错误：{e}")
        
        return


def concat_videos(video_list, output):
    with open(".video_list.txt", "w") as f:
        for video in video_list:
            f.write(f"file '{video}'\n")
    
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', '.video_list.txt',
        '-c', 'copy',
        output
    ]
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"视频合并成功，保存至 {output}")
    except subprocess.CalledProcessError as e:
        print(f"视频合并过程中出现错误：{e}")
        
        return

def get_working_dir():
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M")
    working_dir = os.path.join("data", formatted_now)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    return working_dir



if uploaded_files:
    if len(uploaded_files) > 10:
        st.error('超过最大限制 10', icon="🚨")
        st.stop()
    working_dir = get_working_dir()
    st.subheader(f"共上传了 {len(uploaded_files)} 张图片：")
    for uploaded_file in uploaded_files:
        st.write(uploaded_file.name)
        
        video_path = os.path.join(working_dir, "video")
        video_fade_path = os.path.join(working_dir, "video_fade")
        img_path = os.path.join(working_dir, "img")
        for path in [video_path, video_fade_path, img_path]:
            if not os.path.exists(path):
                os.makedirs(path)
        
        save_path = os.path.join(img_path, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())

    st.subheader('子视频：')
    columns = st.columns(min(len(uploaded_files), 3))
    for img_file in uploaded_files:
        img_path = os.path.join(working_dir, "img", img_file.name)
        video_path = os.path.join(working_dir, "video", img_file.name.split(".")[0] + ".mp4")
        fade_path = os.path.join(working_dir, "video_fade", img_file.name.split(".")[0] + "_fade.mp4")
        gen_video_by_img(img_path, video_path, fade_path)
        
        with columns[uploaded_files.index(img_file)%5]:
            st.write('「{}」'.format(img_file.name))
            st.video(video_path)
        
    
    video_list = [os.path.join(working_dir, "video_fade", img_file.name.split(".")[0] + "_fade.mp4") for img_file in uploaded_files]
    concat_video_path = os.path.join(working_dir, "output.mp4")
    concat_videos(video_list, concat_video_path)
    st.subheader('最终的的视频')
    st.video(concat_video_path)
