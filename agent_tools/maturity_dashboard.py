import os
import pandas as pd
import numpy as np
import cv2
import plotly.graph_objects as go
import gradio as gr
from plotly.subplots import make_subplots

# ==========================================
# 📐 座標投影與配置設定
# ==========================================
REAL_L = 23.0    # 田長 (m)
REAL_W = 18.0    # 田寬 (m)
IMAGE_CORNERS = [(8, 9), (1138, 5), (1174, 838), (18, 812)]
COLOR_PALETTE = {
    0: "#388E3C",  # 綠 (Unripe)
    1: "#FBC02D",  # 白/黃 (Semi-ripe)
    2: "#D32F2F"   # 紅 (Ripe)
}
CLASS_NAMES = {0: "綠色 (未熟)", 1: "白色 (半熟)", 2: "紅色 (完熟)"}

def get_projection_matrix():
    src_pts = np.array(IMAGE_CORNERS, dtype=np.float32)
    dst_pts = np.array([[0,0], [REAL_W,0], [REAL_W,REAL_L], [0,REAL_L]], dtype=np.float32)
    return cv2.findHomography(src_pts, dst_pts)[0]

H = get_projection_matrix()

def pixel_to_real(u, v):
    pixel_pt = np.array([[[u, v]]], dtype=np.float32)
    ground_pos = cv2.perspectiveTransform(pixel_pt, H)[0][0]
    return ground_pos[0], ground_pos[1]

# ==========================================
# 📊 資料處理邏輯
# ==========================================
def load_and_process_data(file_path=None):
    if file_path is None or not os.path.exists(file_path):
        # 產生模擬數據供展示
        np.random.seed(42)
        data = {
            'frame': np.arange(1, 501),
            'track_id': np.random.randint(1, 100, 500),
            'x1': np.random.randint(50, 1100, 500),
            'y1': np.random.randint(50, 800, 500),
            'x2': 0, 'y2': 0,
            'confidence': np.random.rand(500),
            'class': np.random.choice([0, 1, 2], 500, p=[0.4, 0.3, 0.3])
        }
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(file_path)

    # 座標轉換
    df['real_x'], df['real_y'] = zip(*df.apply(lambda row: pixel_to_real(row['x1'], row['y1']), axis=1))
    
    # 根據 track_id 取最後一次出現的位置與類別 (去重)
    df_unique = df.sort_values('frame').groupby('track_id').last().reset_index()
    
    # 區塊聚合 (每 2 公尺一個區塊)
    df_unique['zone_x'] = (df_unique['real_x'] // 2.0) * 2 + 1
    df_unique['zone_y'] = (df_unique['real_y'] // 2.0) * 2 + 1
    df_unique['zone_id'] = df_unique['zone_x'].astype(str) + "_" + df_unique['zone_y'].astype(str)
    
    return df_unique

# ==========================================
# 🎨 視覺化圖表生成
# ==========================================
def create_map_plot(df):
    # 聚合區塊數據
    zone_stats = df.groupby(['zone_x', 'zone_y', 'zone_id']).agg(
        total=('class', 'count'),
        dominant_cls=('class', lambda x: x.value_counts().index[0])
    ).reset_index()

    fig = go.Figure()

    # 1. 畫出農田背景 (簡化版)
    fig.add_shape(type="rect", x0=0, y0=0, x1=REAL_W, y1=REAL_L, 
                  fillcolor="#D2B48C", opacity=0.3, layer="below", line_width=0)

    # 2. 畫出成熟度區塊點
    for _, row in zone_stats.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['zone_x']], y=[row['zone_y']],
            mode='markers',
            marker=dict(size=25, color=COLOR_PALETTE[row['dominant_cls']], 
                        line=dict(width=2, color='white')),
            name=f"Zone {row['zone_id']}",
            customdata=[row['zone_id']],
            hovertemplate="區塊: %{customdata}<br>總數: " + str(row['total']) + "<extra></extra>"
        ))

    fig.update_layout(
        title="🍓 草莓熟度分佈地圖 (點擊區塊查看詳情)",
        xaxis=dict(title="寬度 (m)", range=[0, REAL_W]),
        yaxis=dict(title="長度 (m)", range=[0, REAL_L]),
        width=700, height=600,
        showlegend=False,
        plot_bgcolor='white',
        clickmode='event+select'
    )
    return fig

def create_donut_chart(df, zone_id=None):
    if zone_id:
        filtered_df = df[df['zone_id'] == zone_id]
        title = f"區塊 {zone_id} 成熟度占比"
    else:
        filtered_df = df
        title = "全區成熟度總佔比"

    counts = filtered_df['class'].value_counts().sort_index()
    labels = [CLASS_NAMES[i] for i in counts.index]
    values = counts.values
    colors = [COLOR_PALETTE[i] for i in counts.index]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, 
                                 marker=dict(colors=colors),
                                 textinfo='percent+label')])
    fig.update_layout(title=title, height=400, showlegend=True)
    return fig

# ==========================================
# 🚀 Gradio 介面建構
# ==========================================
def build_dashboard(file_obj=None):
    file_path = file_obj.name if file_obj else None
    df = load_and_process_data(file_path)
    
    # 初始圖表
    map_fig = create_map_plot(df)
    total_donut = create_donut_chart(df)
    
    total_count = len(df)
    red_count = len(df[df['class'] == 2])
    
    summary_text = f"### 📊 統計摘要\n- **總草莓數**: {total_count} 顆\n- **完熟(紅)數量**: {red_count} 顆\n- **平均成熟率**: {red_count/total_count:.1%}"
    
    return map_fig, total_donut, summary_text, df

def on_map_click(click_data, df_state):
    if not click_data or 'points' not in click_data:
        return create_donut_chart(df_state)
    
    zone_id = click_data['points'][0]['customdata']
    return create_donut_chart(df_state, zone_id)

with gr.Blocks(title="草莓數位孿生監控系統", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🍓 草莓成熟度監控儀表板 (Strawberry Digital Twin)")
    gr.Markdown("---")
    
    df_state = gr.State()
    
    with gr.Row():
        with gr.Column(scale=3):
            map_plot = gr.Plot(label="互動地圖")
        with gr.Column(scale=2):
            summary_md = gr.Markdown()
            detail_plot = gr.Plot(label="區域成熟度分析")
    
    with gr.Row():
        file_input = gr.File(label="匯入偵測紀錄檔 (.txt)", file_types=[".txt", ".csv"])
        refresh_btn = gr.Button("🔄 重新載入數據", variant="primary")

    # 點擊地圖更新圓環圖
    map_plot.select(on_map_click, inputs=[df_state], outputs=[detail_plot])
    
    # 重新載入數據
    refresh_btn.click(build_dashboard, inputs=[file_input], 
                     outputs=[map_plot, detail_plot, summary_md, df_state])
    
    # 初始化
    demo.load(build_dashboard, inputs=[file_input], 
              outputs=[map_plot, detail_plot, summary_md, df_state])

if __name__ == "__main__":
    demo.launch()
