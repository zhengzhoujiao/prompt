import os
import sys
import json
import requests
from urllib.parse import unquote

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 读取同级目录下的 prompt.json
_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.json")
with open(_json_path, "r", encoding="utf-8") as _f:
    raw_json_data = _f.read()

def download_file(url, save_path):
    """通用下载函数"""
    try:
        # 对URL进行解码处理，防止特殊字符报错
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  [成功] 已保存: {save_path}")
    except Exception as e:
        print(f"  [失败] 下载 {url} 出错: {e}")

def main():
    # 解析JSON
    categories = json.loads(raw_json_data)
    
    # 根目录名
    root_dir = "downloads"
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    for category in categories:
        cat_name = category.get('name', 'unknown_category')
        projects = category.get('projects', [])
        
        print(f"正在处理分类: {cat_name}")
        
        for project in projects:
            # 清理标题中的特殊字符（防止作为文件夹名时报错）
            proj_title = project.get('title', 'unknown_project').replace('/', '_').replace('\\', '_')
            
            # 建立本地目录结构: downloads/分类名/项目名/
            local_dir = os.path.join(root_dir, cat_name, proj_title)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            
            # 1. 下载图片列表
            for img_url in project.get('imgs', []):
                # 从URL获取文件名（如 预览图.webp）
                img_name = unquote(os.path.basename(img_url))
                img_save_path = os.path.join(local_dir, img_name)
                download_file(img_url, img_save_path)
            
            # 2. 下载 meta.json 文件
            meta_url = project.get('meta_path')
            if meta_url:
                meta_name = unquote(os.path.basename(meta_url))
                meta_save_path = os.path.join(local_dir, meta_name)
                download_file(meta_url, meta_save_path)

if __name__ == "__main__":
    main()