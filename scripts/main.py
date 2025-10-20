from functions import searchChunk, Answer_question

import streamlit as st


DATABASE_PATH = "code/RAG/chroma_data"

# Streamlit UI
# Streamlit ページの構築
st.title("RAG 質問応答システム")

# 質問入力欄
user_question = st.text_input("質問を入力してください:", "")

# 件数指定
N = st.slider("表示する関連チャンクの数:", min_value=1, max_value=10, value=3, step=1)

# ボタンを押して質問を処理
if st.button("検索"):
    if user_question.strip() == "":
        st.warning("質問を入力してください。")
    else:
        try:
            docs, urls = searchChunk(DATABASE_PATH, user_question, N)

            ans, error_flg = Answer_question(user_question, docs)

            if not error_flg:
                st.subheader("回答")
            else:
                st.subheader("エラー")
            st.write(ans)

            st.subheader("関連する URL")
            st.markdown("\n".join([f"- [{url}]({url})" for url in urls]))

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")