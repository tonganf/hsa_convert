import os
import pickle
from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# Đường dẫn đến thư mục chứa các model
MODEL_DIR = 'models'
MODEL_FILES = {
    'A00': 'model_A00.pkl',
    'A01': 'model_A01.pkl',
    'B00': 'model_B00.pkl',
    'C00': 'model_C00.pkl',
    'D01': 'model_D01.pkl'
}

# Load các model khi ứng dụng khởi động
models = {}
for combo, filename in MODEL_FILES.items():
    filepath = os.path.join(MODEL_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as f:
                models[combo] = pickle.load(f)
                print(f"Đã tải model cho tổ hợp: {combo}")
        except Exception as e:
            print(f"Lỗi khi tải model {filename}: {e}")
            # Có thể thêm xử lý lỗi ở đây, ví dụ dừng ứng dụng hoặc bỏ qua model lỗi
    else:
        print(f"Cảnh báo: Không tìm thấy file model {filename}")
        # Đặt model thành None để kiểm tra sau
        models[combo] = None

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    input_hsa_score = "" # Giữ lại giá trị nhập liệu

    if request.method == 'POST':
        input_hsa_score = request.form.get('hsa_score', '').strip()
        if not input_hsa_score:
             error = "Vui lòng nhập điểm HSA."
        else:
            try:
                # Chuyển đổi input sang số float
                hsa_score = float(input_hsa_score)

                # Kiểm tra điểm hợp lệ (ví dụ: thang điểm HSA thường từ 30-150)
                # Bạn nên điều chỉnh khoảng giá trị này nếu cần
                if not (30 <= hsa_score <= 150):
                     raise ValueError("Điểm HSA không hợp lệ (cần trong khoảng 30-150).")

                results = []
                for combo, model in models.items():
                    if model:
                        try:
                            # Giả định model nhận input là [[score]]
                            # Điều chỉnh dòng này nếu model của bạn nhận input khác
                            predicted_score = model.predict([[hsa_score]])[0]
                            # Làm tròn đến 2 chữ số thập phân
                            results.append({
                                'combination': combo,
                                'score': round(predicted_score, 2)
                            })
                        except Exception as predict_error:
                            print(f"Lỗi khi dự đoán với model {combo}: {predict_error}")
                            # Hiển thị lỗi hoặc giá trị mặc định nếu không dự đoán được
                            results.append({
                                'combination': combo,
                                'score': 'Lỗi'
                            })
                    else:
                         # Trường hợp model không được tải thành công
                         results.append({
                            'combination': combo,
                            'score': 'N/A'
                        })


            except ValueError as ve:
                error = f"Dữ liệu nhập không hợp lệ: {ve}. Vui lòng nhập một số."
            except Exception as e:
                error = f"Đã xảy ra lỗi không mong muốn: {e}"

    # Truyền cả input_hsa_score vào template để hiển thị lại
    return render_template('index.html', results=results, error=error, hsa_score=input_hsa_score)

if __name__ == '__main__':
    # debug=True chỉ nên dùng khi phát triển, tắt khi triển khai thực tế
    app.run(debug=True)