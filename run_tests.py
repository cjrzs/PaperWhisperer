#!/usr/bin/env python
"""
测试运行脚本
检查依赖并提供友好的错误提示
"""
import sys
import subprocess

def check_dependencies():
    """检查必要的依赖"""
    missing = []
    
    # 检查测试框架
    try:
        import pytest
        print("✅ pytest 已安装")
    except ImportError:
        missing.append("pytest")
    
    try:
        import pytest_asyncio
        print("✅ pytest-asyncio 已安装")
    except ImportError:
        missing.append("pytest-asyncio")
    
    # 检查 pymilvus
    try:
        import pymilvus
        print("✅ pymilvus 已安装")
        can_run_all = True
    except ImportError:
        print("⚠️  pymilvus 未安装 - 将无法运行完整测试")
        print("   提示: 可以切换到 Python 3.10 环境后安装完整依赖")
        can_run_all = False
    
    if missing:
        print("\n❌ 缺少以下依赖:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n请运行: pip install " + " ".join(missing))
        return False, False
    
    return True, can_run_all

def main():
    """主函数"""
    print("="*60)
    print("PaperWhisperer - 测试运行器")
    print("="*60)
    print()
    
    # 检查 Python 版本
    py_version = sys.version_info
    print(f"Python 版本: {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    if py_version.major == 3 and py_version.minor >= 13:
        print("⚠️  警告: Python 3.13 可能存在依赖兼容性问题")
        print("   建议: 使用 Python 3.10 以获得最佳体验")
    
    print()
    
    # 检查依赖
    has_test_deps, can_run_all = check_dependencies()
    
    if not has_test_deps:
        return 1
    
    print()
    print("="*60)
    
    if not can_run_all:
        print("⚠️  由于缺少 pymilvus，无法运行完整测试")
        print()
        print("📝 解决方案:")
        print("1. 切换到 Python 3.10:")
        print("   conda create -n paperwhisperer python=3.10 -y")
        print("   conda activate paperwhisperer")
        print("   pip install -r requirements.txt")
        print()
        print("2. 使用 Docker:")
        print("   docker-compose up -d")
        print("   docker-compose exec backend pytest test_milvus_service.py -v")
        print()
        print("3. 手动安装 pymilvus（可能失败）:")
        print("   pip install pymilvus==2.3.3")
        print("="*60)
        return 1
    
    # 运行测试
    print("🚀 开始运行测试...")
    print("="*60)
    print()
    
    # 构建 pytest 命令
    cmd = [sys.executable, "-m", "pytest", "test_milvus_service.py", "-v"]
    
    # 添加命令行参数
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # 运行测试
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

