import os
import pandas as pd
from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# ==============================================================
# CẤU HÌNH VÀ TẢI DATAFRAME TỪ EXCEL

# *** QUAN TRỌNG: Sửa lại các KEY (tên cột trong file Excel) cho đúng ***
COLUMN_MAPPING = {
    'A00_2024': 'A00',
    'A01_2024': 'A01',
    'B00_2024': 'B00',
    '2024_D01': 'D01',
    'C00_2024': 'C00',
}

# Các tổ hợp mục tiêu cần hiển thị (theo thứ tự)
TARGET_COMBINATIONS = ['A00', 'A01', 'D01', 'D07', 'B00']

# Đường dẫn đến file Excel
EXCEL_FILE_PATH = '2023-2024.xlsx'

# Hàm tải và chuẩn bị DataFrame
def load_and_prepare_data(filepath):
    try:
        # Đọc file Excel (cần cài openpyxl)
        df = pd.read_excel(filepath)

        # *** Kiểm tra xem cột 'HSA' có tồn tại không (sửa tên nếu cần) ***
        hsa_column_name = 'HSA'  # Giả sử tên cột là 'HSA'
        if hsa_column_name not in df.columns:
            print(f"Lỗi: Cột '{hsa_column_name}' không tồn tại trong file Excel.")
            return None

        # Loại bỏ các dòng có giá trị NaN trong cột HSA (nếu có)
        df.dropna(subset=[hsa_column_name], inplace=True)

        # Chuyển cột HSA thành số nguyên
        try:
            df[hsa_column_name] = df[hsa_column_name].astype(int)
        except ValueError as ve:
            print(f"Lỗi: Không thể chuyển đổi cột '{hsa_column_name}' thành số nguyên. Kiểm tra dữ liệu. Lỗi: {ve}")
            return None

        # Đặt cột 'HSA' làm index để tra cứu nhanh
        df.set_index(hsa_column_name, inplace=True)
        return df

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file dữ liệu tại '{filepath}'")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc hoặc xử lý file {filepath}: {e}")
        return None

# Tải và chuẩn bị DataFrame một lần khi ứng dụng khởi động
conversion_df = load_and_prepare_data(EXCEL_FILE_PATH)
# ==============================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    input_hsa_score_str = ""  # Giữ lại giá trị nhập liệu dạng chuỗi

    # Kiểm tra xem DataFrame đã được tải thành công chưa
    if conversion_df is None:
        error = "Lỗi hệ thống: Không thể tải hoặc xử lý dữ liệu quy đổi. Vui lòng kiểm tra lại file dữ liệu hoặc liên hệ quản trị viên."
        if request.method == 'POST':
            input_hsa_score_str = request.form.get('hsa_score', '').strip()
        return render_template('index.html', results=None, error=error, hsa_score=input_hsa_score_str)

    if request.method == 'POST':
        input_hsa_score_str = request.form.get('hsa_score', '').strip()
        if not input_hsa_score_str:
            error = "Vui lòng nhập điểm HSA."
        else:
            try:
                # Chuyển đổi input sang số để kiểm tra
                hsa_score_float = float(input_hsa_score_str)
                hsa_score_int = int(hsa_score_float)

                # Kiểm tra giới hạn 0-150
                if not (0 <= hsa_score_int <= 150):
                    error = "Điểm HSA phải nằm trong khoảng từ 0 đến 150."
                else:
                    # Tra cứu điểm trong DataFrame bằng index (HSA)
                    score_data_series = conversion_df.loc[hsa_score_int]  # Trả về một Pandas Series

                    results = []
                    for combo in TARGET_COMBINATIONS:
                        # Tìm tên cột gốc trong Excel tương ứng với tổ hợp 'combo'
                        original_col_name = None
                        for excel_col, target_combo in COLUMN_MAPPING.items():
                            if target_combo == combo:
                                original_col_name = excel_col
                                break

                        converted_score = 'N/A'  # Mặc định là N/A
                        # Kiểm tra xem cột gốc có tồn tại trong df và có trong kết quả tra cứu không
                        if original_col_name and original_col_name in conversion_df.columns:
                            # Lấy giá trị từ Series và làm tròn nếu là số
                            value = score_data_series[original_col_name]
                            if pd.notna(value) and isinstance(value, (int, float)):
                                converted_score = round(value, 2)  # Làm tròn 2 chữ số thập phân
                            elif pd.notna(value):
                                converted_score = value  # Giữ nguyên nếu không phải số

                        results.append({
                            'combination': combo,
                            'score': converted_score
                        })

            except ValueError:
                # Lỗi nếu người dùng nhập không phải là số
                error = "Dữ liệu nhập không hợp lệ. Vui lòng chỉ nhập số."
            except KeyError:
                # Lỗi nếu điểm HSA (hsa_score_int) không có trong index của DataFrame
                error = f"Không tìm thấy dữ liệu quy đổi cho điểm HSA = {input_hsa_score_str} trong bảng."
                # Hiển thị bảng trống với N/A
                results = []
                for combo in TARGET_COMBINATIONS:
                    results.append({'combination': combo, 'score': 'N/A'})
            except Exception as e:
                error = f"Đã xảy ra lỗi không mong muốn: {e}"
                print(f"Unhandled exception: {e}")

    # Truyền cả input_hsa_score_str vào template để hiển thị lại
    return render_template('index.html',
                           results=results,
                           error=error,
                           hsa_score=input_hsa_score_str)

if __name__ == '__main__':
    app.run(debug=True)  # Tắt debug=True khi triển khai thực tế