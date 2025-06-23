#removed the progess bar for now. not really necessary
import streamlit as st
import sqlite3
from datetime import datetime
import time
import random

conn = sqlite3.connect('orders.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        item TEXT,
        quantity INTEGER
    )
''')
conn.commit()

st.set_page_config(page_title="Izakaya Honoo", page_icon="🍶", layout="centered")

lang = st.radio("Language / 言語", ["English", "日本語"], horizontal=True)

daily_specials = [
    ("刺身盛り合わせ (Sashimi Platter)", 1200),
    ("銀だら西京焼き (Grilled Miso Black Cod)", 900),
    ("明太子クリームうどん (Mentaiko Cream Udon)", 850),
    ("鯖の味噌煮 (Miso Simmered Mackerel)", 750),
    ("抹茶アイス (Matcha Ice Cream)", 400)
]

if "todays_special" not in st.session_state:
    st.session_state.todays_special = random.choice(daily_specials)

todays_special = st.session_state.todays_special

menu_items = {
    "焼き鳥 (Yakitori)": 300,
    "枝豆 (Edamame)": 200,
    "たこ焼き (Takoyaki)": 450,
    "唐揚げ (Karaage)": 400,
    "お好み焼き (Okonomiyaki)": 600,
    "ビール (Beer)": 500,
    "ウーロン茶 (Oolong Tea)": 250
}
menu_items[todays_special[0]] = todays_special[1]

menu_keywords = {
    "yakitori": "焼き鳥 (Yakitori)",
    "edamame": "枝豆 (Edamame)",
    "takoyaki": "たこ焼き (Takoyaki)",
    "karaage": "唐揚げ (Karaage)",
    "okonomiyaki": "お好み焼き (Okonomiyaki)",
    "beer": "ビール (Beer)",
    "oolongtea": "ウーロン茶 (Oolong Tea)",
    "oolong": "ウーロン茶 (Oolong Tea)",
    "tea": "ウーロン茶 (Oolong Tea)",
    "special": todays_special[0]
}

if "cart" not in st.session_state:
    st.session_state.cart = {}
if not isinstance(st.session_state.cart, dict):
    st.session_state.cart = {}

if "pending_items" not in st.session_state:
    st.session_state.pending_items = {}
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False

TXT = {
    "English": {
        "title": "🍶 Izakaya Honoo",
        "subtitle": "Welcome to our cozy Japanese Izakaya",
        "menu": "📜 Today's Menu",
        "order": "🧾 Place Your Order",
        "next": "✅ Next: Choose Quantities",
        "quantities": "How many of each item?",
        "add_to_cart": "🛒 Add to Cart",
        "cart": "🛒 Your Cart",
        "total": "💰 Total",
        "remove": "Remove",
        "modify": "Change Quantity",
        "place_order": "📦 Place Order",
        "thank_you": "🎉 Thank you for your order!",
        "reset": "🗑️ Reset Cart",
        "new_order": "🔁 New Order",
        "invalid": "❌ Invalid item:",
        "please_enter": "Please enter at least one item.",
        "pay_now": "💳 Pay Now",
        "pay_disabled": "No orders to pay yet.",
        "final_message": "🎉 Thank you for coming. See you next time!\n\nThe page will reset automatically in 5 seconds.",
        "enter_items": "Enter items (e.g. yakitori, beer. For the special you can also type special):",
        "previous_orders": "📜 Previous Orders",
        "paid_at": "Paid at"
    },
    "日本語": {
        "title": "🍶 居酒屋 炎",
        "subtitle": "いらっしゃいませ！ゆったりしていってね",
        "menu": "📜 今日のメニュー",
        "order": "🧾 ご注文はこちら",
        "next": "✅ 次へ: 数量を選択",
        "quantities": "商品の数を選んでね",
        "add_to_cart": "🛒 カートに追加",
        "cart": "🛒 あなたのカート",
        "total": "💰 合計",
        "remove": "削除",
        "modify": "数を変更",
        "place_order": "📦 注文確定",
        "thank_you": "🎉 ご注文ありがとうございました！",
        "reset": "🗑️ リセット",
        "new_order": "🔁 新しい注文",
        "invalid": "❌ 無効な項目:",
        "please_enter": "最低1つは入力してね",
        "pay_now": "💳 お会計",
        "pay_disabled": "まだ注文がありません。",
        "final_message": "🎉 ご来店ありがとうございました！またのお越しをお待ちしております。\n\n5秒後に画面がリセットされます。",
        "enter_items": "商品名を入力してね（例: yakitori, beer。スペシャルは special と入力可）:",
        "previous_orders": "📜 過去の注文",
        "paid_at": "お会計時間"
    }
}
T = TXT[lang]

st.markdown(f"<h1 style='text-align: center;'>{T['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>{T['subtitle']}</h4>", unsafe_allow_html=True)
st.markdown("___")

st.markdown(f"### {T['menu']}")
cols = st.columns(2)
st.markdown(f"### Today's Special: {todays_special[0]} — ¥{todays_special[1]}")
for idx, (item, price) in enumerate(menu_items.items()):
    with cols[idx % 2]:
        st.markdown(f"<div style='padding:4px 0px;'>• <strong>{item}</strong> — ¥{price}</div>", unsafe_allow_html=True)
st.markdown("___")

if not st.session_state.order_placed:
    st.markdown(f"### {T['order']}")
    user_input = st.text_input(T['enter_items'])

    if st.button(T['next']):
        if user_input:
            cleaned_input = [word.strip().lower().replace(" ", "") for word in user_input.split(",")]
            st.session_state.pending_items = {}
            for word in cleaned_input:
                if word in menu_keywords:
                    name = menu_keywords[word]
                    st.session_state.pending_items[name] = 1
                else:
                    st.warning(f"{T['invalid']} {word}")
        else:
            st.info(T['please_enter'])

if st.session_state.pending_items and not st.session_state.order_placed:
    st.markdown(f"### {T['quantities']}")
    running_total = 0
    for item in list(st.session_state.pending_items.keys()):
        qty = st.selectbox(
            f"{item} - Quantity:",
            options=list(range(1, 11)),
            index=st.session_state.pending_items[item] - 1,
            key=f"qty_{item}"
        )
        st.session_state.pending_items[item] = qty
        running_total += qty * menu_items[item]

    st.info(f"{T['total']}: ¥{running_total}")

    if st.button(T['add_to_cart']):
        for item, qty in st.session_state.pending_items.items():
            st.session_state.cart[item] = st.session_state.cart.get(item, 0) + qty
        st.success("Items added to cart!")
        st.session_state.pending_items = {}

if st.session_state.cart:
    st.markdown(f"### {T['cart']}")
    total_price = 0
    to_remove = []

    for item, qty in st.session_state.cart.items():
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**{item}** × {qty} = ¥{qty * menu_items[item]}")
        with col2:
            new_qty = st.selectbox(T['modify'], list(range(1, 11)), index=qty - 1, key=f"mod_{item}")
            st.session_state.cart[item] = new_qty
        with col3:
            if st.button(T['remove'], key=f"rem_{item}"):
                to_remove.append(item)

    for item in to_remove:
        del st.session_state.cart[item]

    total_price = sum(qty * menu_items[item] for item, qty in st.session_state.cart.items())
    st.markdown(f"### {T['total']}: ¥{total_price}")

if not st.session_state.order_placed:
    if st.button(T['place_order']):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item, qty in st.session_state.cart.items():
            c.execute('INSERT INTO orders (timestamp, item, quantity) VALUES (?, ?, ?)',
                      (timestamp, item, qty))
        conn.commit()

        order_id = c.execute('SELECT MAX(id) FROM orders').fetchone()[0]
        st.session_state.order_placed = True
        st.success(f"{T['thank_you']} \n\nYour order number: {order_id}")

reset_label = T['reset'] if not st.session_state.order_placed else T['new_order']
if st.button(reset_label):
    st.session_state.cart = {}
    st.session_state.order_placed = False
    st.session_state.pending_items = {}
    st.session_state.clear()
    st.rerun()

st.markdown(f"### {T['previous_orders']}")
orders = c.execute('SELECT timestamp, item, quantity FROM orders ORDER BY id DESC LIMIT 10').fetchall()

for order in orders:
    st.write(f"{order[0]} — {order[1]} x {order[2]}")

orders_exist = c.execute('SELECT COUNT(*) FROM orders').fetchone()[0] > 0
if orders_exist:
    if st.button(T['pay_now']):
        c.execute('DELETE FROM orders')
        conn.commit()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"{T['final_message']} \n\n{T['paid_at']}: {now}")

        time.sleep(5)

        st.session_state.cart = {}
        st.session_state.pending_items = {}
        st.session_state.order_placed = False
        st.session_state.clear()
        st.rerun()
else:
    st.button(T['pay_now'], disabled=True, help=T['pay_disabled'])