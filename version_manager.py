#!/usr/bin/env python3
"""
版本管理脚本
用于递增程序版本号
"""

import re
import sys

def increment_version_in_file(file_path, increment=0.01):
    """递增指定文件中的版本号"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找版本号定义
        version_pattern = r'(__version__\s*=\s*")(\d+\.\d+)(")'
        match = re.search(version_pattern, content)
        
        if match:
            current_version = float(match.group(2))
            new_version = current_version + increment
            new_version_str = f"{new_version:.2f}"
            
            # 替换版本号
            new_content = re.sub(
                version_pattern,
                f'\\g<1>{new_version_str}\\g<3>',
                content
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"版本号已更新: {match.group(2)} -> {new_version_str}")
            return new_version_str
        else:
            print("未找到版本号定义")
            return None
            
    except Exception as e:
        print(f"更新版本号时出错: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("用法: python version_manager.py <文件路径> [递增量]")
        print("示例: python version_manager.py main.py 0.01")
        return
    
    file_path = sys.argv[1]
    increment = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
    
    new_version = increment_version_in_file(file_path, increment)
    
    if new_version:
        print(f"建议提交信息: 版本更新至 v{new_version}")

if __name__ == "__main__":
    main()