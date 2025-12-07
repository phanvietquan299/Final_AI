# Task 2: Adversarial Search - Go Game (9x9)

## Luật chơi Go 9x9
1. **Mục tiêu:** Chiếm nhiều lãnh thổ hơn đối thủ bằng cách bao vây vùng trống.
2. **Bắt quân:** Một nhóm bị bắt khi không còn khí (các điểm trống liền kề toàn bị đối phương chiếm).
3. **Ko rule:** Không được lặp lại đúng vị trí bàn cờ vừa xảy ra ở lượt trước, tránh vòng lặp vô hạn.
4. **Suicide rule:** Không được đặt quân khiến nhóm của mình mất hết khí trừ khi bắt được quân đối phương.
5. **Kết thúc:** Cả hai người chơi chọn “Pass” liên tiếp.
6. **Tính điểm:** Stones + Territory + Komi (White được cộng 6.5 điểm vì đi sau).

## Hướng dẫn chơi
- **Cài đặt:** `pip install -r requirements.txt`
- **Khởi động:** `python main.py`
- **Chế độ chơi:** Dùng nút `PvP` để chơi hai người, `PvAI` để chơi với AI.
- **Đặt quân:** Click vào ô trống trên bàn 9x9 để đặt quân hiện tại.
- **Pass:** Nhấn nút “Pass” để bỏ lượt.
- **New Game:** Nhấn “New Game” để bắt đầu ván mới.
- **Thông tin:** Bảng bên phải hiển thị lượt hiện tại, điểm số và trạng thái game.

## Ghi chú
- UI sử dụng Pygame nên tương tác bằng chuột.
- AI dùng Minimax + Alpha-Beta nên một nước đi có thể mất vài giây tùy cấu hình depth/time. Có thể chỉnh `depth` hoặc `time_limit` trong `src/ui/game_ui.py` nếu cần phản hồi nhanh hơn.
