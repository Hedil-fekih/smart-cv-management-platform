#!/usr/bin/env python3
"""
Smart CV Management Platform
Run this file to start the server accessible from any network
"""

from app import app
import os
import socket
import subprocess
import sys
import time
import threading

def get_network_ip():
    """Get the actual network IP address"""
    try:
        # Connect to a remote address to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback method
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

def install_ngrok():
    """Install ngrok if not present"""
    try:
        subprocess.run(["ngrok", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing ngrok for public access...")
        try:
            # Try to install ngrok via pip
            subprocess.run([sys.executable, "-m", "pip", "install", "pyngrok"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Could not install ngrok automatically")
            print("   Please install manually: pip install pyngrok")
            return False

def start_ngrok_tunnel():
    """Start ngrok tunnel in background"""
    try:
        from pyngrok import ngrok
        public_tunnel = ngrok.connect(5000)
        public_url = public_tunnel.public_url
        return public_url
    except ImportError:
        return None
    except Exception as e:
        print(f"⚠️  Could not create public tunnel: {e}")
        return None

if __name__ == '__main__':
    local_ip = get_network_ip()
    
    print("=" * 70)
    print("🚀 Smart CV Management Platform Starting...")
    print("=" * 70)
    
    public_url = None
    if install_ngrok():
        print("🌍 Creating public tunnel for global access...")
        public_url = start_ngrok_tunnel()
    
    print(f"📍 Local access: http://localhost:5000")
    print(f"📍 Local access: http://127.0.0.1:5000")
    print(f"🌐 Network access: http://{local_ip}:5000")
    print(f"📱 Mobile/Tablet access: http://{local_ip}:5000")
    
    if public_url:
        print("=" * 70)
        print("🌍 PUBLIC ACCESS (works from ANY network/device):")
        print(f"🔗 {public_url}")
        print("   ✅ Share this link with anyone, anywhere!")
        print("   ✅ Works on any phone, tablet, computer")
        print("   ✅ No need for same WiFi network")
    else:
        print("=" * 70)
        print("⚠️  Public access not available (ngrok not installed)")
        print("   Install with: pip install pyngrok")
    
    print("=" * 70)
    print("🔥 IMPORTANT: If you can't access from phone/other devices:")
    print("   1. Make sure your firewall allows port 5000")
    print("   2. Try disabling Windows Firewall temporarily")
    print("   3. Use the PUBLIC URL above for global access")
    print("=" * 70)
    print("✅ Platform ready! Starting server...")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    # Run the app accessible from any network
    try:
        app.run(
            debug=False,        # Disabled debug for better network performance
            host='0.0.0.0',     # Accept connections from any IP
            port=5000,
            threaded=True,      # Handle multiple requests simultaneously
            use_reloader=False  # Prevent double startup in network mode
        )
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ ERROR: Port 5000 is already in use!")
            print("   Try: python run.py --port 8080")
            print("   Or kill the process using port 5000")
        else:
            print(f"❌ ERROR: {e}")
            print("   Try running as administrator/sudo")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        try:
            from pyngrok import ngrok
            ngrok.kill()
        except:
            pass
