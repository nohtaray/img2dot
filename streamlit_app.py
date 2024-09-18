import streamlit as st
import numpy as np
from PIL import Image
import io
import csv
from matplotlib import pyplot as plt


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def find_closest_color(pixel, color_palette):
    return min(color_palette, key=lambda c: sum((int(a) - int(b)) ** 2 for a, b in zip(pixel, c)))


def image_to_pixel_art(image, color_palette, output_size):
    # img = image.resize(output_size, Image.NEAREST)
    img = image.resize(output_size)
    img = img.convert('RGB')
    pixel_data = np.array(img)

    height, width, _ = pixel_data.shape
    result = np.zeros((height, width, 3), dtype=np.uint8)
    index_map = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            closest_color = find_closest_color(pixel_data[y, x], color_palette)
            result[y, x] = closest_color
            index_map[y, x] = color_palette.index(closest_color)
            # result[y, x] = pixel_data[y, x]
            # index_map[y, x] = 0

    return Image.fromarray(result), index_map


st.title("画像をドット絵に変換")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
color_codes = st.text_input("カラーコードをカンマ区切りで入力してください (例: #FF0000,#00FF00,#0000FF)",
                            "#FFFFFF,#D0343A,#073388,#EEFC46,#38CD66")
color_palette = [hex_to_rgb(code.strip()) for code in color_codes.split(",")]
col1, col2 = st.columns(2)
with col1:
    output_width = st.number_input("出力幅", min_value=2, max_value=2048, value=45, step=1)
with col2:
    output_height = st.number_input("出力高さ", min_value=2, max_value=2048, value=67, step=1)

if uploaded_file is not None and color_codes:
    image = Image.open(uploaded_file)

    pixel_art, index_map = image_to_pixel_art(image, color_palette, (output_width, output_height))

    # st.image(pixel_art, caption="変換後のドット絵", use_column_width=True)

    figw = 4
    figh = round(output_height / output_width * figw)
    fig, ax = plt.subplots(figsize=(figw, figh))
    cp2 = []
    for a, b, c in color_palette:
        cp2.append((a / 255, b / 255, c / 255))
    color_map = plt.cm.colors.ListedColormap(cp2)
    ax.imshow(index_map, cmap=color_map, extent=(0, output_width, 0, output_height), vmin=0, vmax=len(color_palette))
    ax.set_xlim(0, output_width)
    ax.set_ylim(0, output_height)
    ax.set_xticks(np.arange(0, output_width + 1, 1))
    ax.set_yticks(np.arange(0, output_height + 1, 1))
    ax.grid(color='black', linestyle='-', linewidth=0.5)
    # Streamlitで画像を更新
    grid_container = st.empty()
    grid_container.pyplot(fig, use_container_width=False)
    # プロットを閉じる
    plt.close(fig)

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(index_map)
    csv_content = csv_buffer.getvalue()
    csv_content = csv_content.replace(',', '\t')

    st.download_button(
        label="CSVファイルをダウンロード",
        data=csv_content,
        file_name="pixel_art_indices.csv",
        mime="text/csv"
    )

    st.text_area("カラーコードのインデックス（CSV形式）", csv_content, height=200)

# カラーパレットのプレビュー
st.subheader("カラーパレットのプレビュー")
palette_preview = Image.new('RGB', (len(color_palette) * 50, 50))
for i, color in enumerate(color_palette):
    for x in range(50):
        for y in range(50):
            palette_preview.putpixel((i * 50 + x, y), color)
st.image(palette_preview, caption="使用カラーパレット", use_column_width=True)
