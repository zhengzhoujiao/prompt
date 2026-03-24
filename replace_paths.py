import os
import json
from urllib.parse import unquote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "prompt.json")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_PATH = os.path.join(BASE_DIR, "prompt_local.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    categories = json.load(f)

for category in categories:
    cat_name = category.get("name", "unknown_category")
    for project in category.get("projects", []):
        proj_title = project.get("title", "unknown_project").replace("/", "_").replace("\\", "_")
        local_dir = os.path.join(DOWNLOADS_DIR, cat_name, proj_title)

        # 替换 imgs（存相对路径，兼容本地和容器）
        new_imgs = []
        for img_url in project.get("imgs", []):
            img_name = unquote(os.path.basename(img_url))
            rel = os.path.join("downloads", cat_name, proj_title, img_name)
            new_imgs.append(rel.replace("\\", "/"))
        project["imgs"] = new_imgs

        # 替换 meta_path
        meta_url = project.get("meta_path")
        if meta_url:
            meta_name = unquote(os.path.basename(meta_url))
            rel = os.path.join("downloads", cat_name, proj_title, meta_name)
            project["meta_path"] = rel.replace("\\", "/")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

print(f"已生成: {OUTPUT_PATH}")
