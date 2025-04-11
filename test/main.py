import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

data = pd.read_excel(r"C:\Users\AnTong\Downloads\2023-2024.xlsx")

# Tạo DataFrame tổng
df = pd.DataFrame(data)

# Tạo 5 DataFrame riêng
df_a00 = df[['HSA', 'A00_2024']]
df_a01 = df[['HSA', 'A01_2024']]
df_b00 = df[['HSA', 'B00_2024']]
df_c00 = df[['HSA', 'C00_2024']]
df_d01 = df[['HSA', '2024_D01']]

# Làm sạch dữ liệu
# Xử lý giá trị lỗi 'Tues' trong df_a00
df_a00.loc[df_a00['A00_2024'] == 'Tues', 'A00_2024'] = 28.82  # Thay bằng giá trị trung bình gần đó
df_a00['A00_2024'] = df_a00['A00_2024'].astype(float)

# Kiểm tra giá trị thiếu
for name, df_temp in [('A00', df_a00), ('A01', df_a01), ('B00', df_b00), ('C00', df_c00), ('D01', df_d01)]:
    print(f"Missing values in {name}:")
    print(df_temp.isnull().sum())
    print()

# Tạo và lưu mô hình cho từng khối
models = {}
for name, df_temp in [('A00', df_a00), ('A01', df_a01), ('B00', df_b00), ('C00', df_c00), ('D01', df_d01)]:
    # Chuẩn bị dữ liệu
    X = df_temp.iloc[:, 1].values.reshape(-1, 1)  # Biến độc lập
    y = df_temp['HSA'].values  # Biến phụ thuộc
    
    # Tạo pipeline với scaling và mô hình
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', LinearRegression())
    ])
    
    # Huấn luyện mô hình
    pipeline.fit(X, y)
    
    # Lưu mô hình
    models[name] = pipeline
    with open(f'model_{name}.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    print(f"Model for {name} created and saved as model_{name}.pkl")

print("All models have been created and saved successfully!")