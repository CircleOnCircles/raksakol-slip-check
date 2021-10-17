import streamlit as st
import pandas as pd
import numpy as np

from functools import lru_cache
import requests
from stqdm import stqdm

stqdm.pandas()

@st.cache
def get_content(url):
    r = requests.get(url, allow_redirects=True)
    return r.content

def get_raw_hash(url):
    return hash(get_content(url))

st.set_page_config(
    page_title="แอพหาภาพสลิปซ้ำ",
    page_icon="🔎",
    menu_items={
        'About': "สร้างโดย @circleoncircles"
    }
)

st.title('แอพหาภาพสลิปซ้ำ')
st.write('สร้างโดย @circleoncircles เพื่อโรงพยาบาลรักษ์สกล')

uploaded_file = st.file_uploader("Choose a csv file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.info('อ่านไฟล์แล้ว')
    
    slip_url_column = st.selectbox('เลือกคอลลัม', [None] + df.columns.tolist())
    if slip_url_column is not None:

        df = df.dropna(subset=[slip_url_column])

        with st.spinner('ทำการโหลดสลิป.. อาจนานถึงสองชั่วโมง+'):
            df['Slip_rawHash'] = df[slip_url_column].progress_apply(get_raw_hash)
        st.success('เรียบร้อย!')

        g = df.groupby(by='Slip_rawHash').filter(lambda x: len(x) > 1).groupby(by='Slip_rawHash')
        st.subheader(f'มีชุดที่ซ้ำกันทั้งหมด {len(g)} ชุด')

        for i, (name, sub_df) in enumerate(g):
            st.header(f"ชุดที่ {i+1}")
            st.dataframe(sub_df)
            with st.expander("ดูสลิปแรก"):
                st.image(sub_df.iloc[0][slip_url_column])
            with st.expander("ดูสลิปทั้งหมด"):
                cols = st.columns(len(sub_df))
                for img_url, col in zip(sub_df[slip_url_column], cols):
                    with col:

                        st.image(img_url)
