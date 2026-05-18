import cv2
import time
import os
import requests
BOT_TOKEN = "8146182188:AAFedvpuXdda4rKzlYSeV8JQf5A29TwRgzk"
CHAT_ID = "6307470883"
SAVE_DIR = "security_caps"
os.makedirs(SAVE_DIR, exist_ok=True)
capture_count = 0
def send_telegram_photo(filepath):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(filepath, "rb") as photo:
        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "caption": "🚨 Motion Detected! Security Camera Alert!"
        }, files={"photo": photo})
    if response.status_code == 200:
        print("Photo sent to Telegram successfully!")
    else:
        print("Failed to send photo:", response.text)
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })
print("Raspberry Pi Security Camera System")
print("Simulated with Laptop Webcam")
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open webcam!")
    exit()
print("Camera initialized successfully!")
time.sleep(2)
send_telegram_message("✅ Security Camera System is now ONLINE!")
print("System armed. Monitoring for motion...")
prev_frame = None
last_capture = 0
cooldown = 10
try:
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to read frame!")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if prev_frame is None:
            prev_frame = gray
            continue
        diff = cv2.absdiff(prev_frame, gray)
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        motion = cv2.countNonZero(thresh)
        cv2.putText(frame, "Security Camera - LIVE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Motion Level: {motion}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if motion > 5000:
            capture_count += 1
            cv2.putText(frame, "MOTION DETECTED!", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            print(f"Motion detected! Level: {motion}")
            if time.time() - last_capture > cooldown:
                ts = time.strftime("%Y%m%d_%H%M%S")
                path = f"{SAVE_DIR}/cap_{ts}.jpg"
                cv2.imwrite(path, frame)
                print(f"Photo captured: {path}")
                send_telegram_photo(path)
                last_capture = time.time()
        cv2.imshow("Security Camera", frame)
        prev_frame = gray
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("System stopped by user!")
            break
except KeyboardInterrupt:
    print("System stopped!")
finally:
    send_telegram_message("🔴 Security Camera System is now OFFLINE!")
    cam.release()
    cv2.destroyAllWindows()
    print("Camera released. Goodbye!")
