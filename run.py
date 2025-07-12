#!/usr/bin/env python3
"""
ChoibenAssist FastAPI Backend - Development Server
開発用サーバー起動スクリプト
"""
import uvicorn
import sys
import os
from pathlib import Path

def main():
    """メイン関数"""
    # プロジェクトルートをPythonパスに追加
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    try:
        from app.core.config import settings
        print(f"🚀 Starting ChoibenAssist AI Backend...")
        print(f"📁 Environment: {settings.environment}")
        print(f"🔧 Debug mode: {settings.debug}")
        print(f"🌐 CORS origins: {settings.allowed_origins}")
        
        # サーバー設定
        config = {
            "app": "app.main:app",
            "host": "127.0.0.1",
            "port": 8000,
            "reload": settings.debug,
            "log_level": "info" if settings.debug else "warning",
            "access_log": settings.debug,
        }
        
        print(f"🌍 Server starting at: http://{config['host']}:{config['port']}")
        print(f"📖 API Documentation: http://{config['host']}:{config['port']}/docs")
        print(f"📚 ReDoc: http://{config['host']}:{config['port']}/redoc")
        print("=" * 60)
        
        # サーバー起動
        uvicorn.run(**config)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Please install required dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        print("💡 Check your .env file and configurations")
        sys.exit(1)


if __name__ == "__main__":
    main()
