import uvicorn
import webbrowser
import threading
import time

def on_startup():
    # Đợi 2 giây cho server khởi động xong
    time.sleep(2) 
    
    # In ra một cái Banner thật ngầu đè lên log của Uvicorn
    print("\n" + "="*60)
    print("🚀 MÁY CHỦ X.509 CA ĐÃ KHỞI ĐỘNG THÀNH CÔNG!")
    print("👉 Mời sếp truy cập API Docs tại: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")
    
    # Tự động mở trình duyệt
    webbrowser.open("http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    # Chạy luồng phụ để in thông báo và mở web
    threading.Thread(target=on_startup).start()
    
    # Chạy Uvicorn (có thể ẩn log mặc định bằng cách thêm log_level="warning", 
    # nhưng khuyên ông cứ để mặc định để dễ debug)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)