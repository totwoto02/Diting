#!/usr/bin/env python3
"""MFS Phase 1 MVP 发布脚本 - 构建 wheel"""
import subprocess
import os

os.chdir("/root/.openclaw/workspace/projects/mfs-memory")

print("=" * 60)
print("MFS Phase 1 MVP 发布 - Step 6: 构建 wheel")
print("=" * 60)

# 构建 wheel
print("\n正在构建 wheel...")
result = subprocess.run(
    ["python3", "setup.py", "bdist_wheel"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("\n✅ wheel 构建成功！")
    print("\n构建产物:")
    subprocess.run(["ls", "-lh", "dist/"])
else:
    print("\n⚠️ wheel 构建失败")
    print(result.stderr[-500:] if result.stderr else "")
    print("\n但 sdist 已存在，可以继续发布流程")

print("\n" + "=" * 60)
