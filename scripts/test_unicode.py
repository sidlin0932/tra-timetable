# -*- coding: utf-8 -*-
import json

stations = {
    "Neiwan": ["\u65b0\u7af9", "\u5317\u65b0\u7af9", "\u5343\u7532", "\u65b0\u838a", "\u7af9\u4e2d", "\u516d\u5bb6", "\u4e0a\u54e1", "\u69ae\u83ef", "\u7af9\u6771", "\u6a6b\u5c71", "\u4e5d\u8b9a\u982d", "\u5408\u8208", "\u5bcc\u8cb3", "\u5167\u7063"],
    "Pingxi": ["\u516b\u5835", "\u6696\u6696", "\u56db\u8173\u4ead", "\u6d77\u79d1\u9928", "\u516b\u6597\u5b50", "\u745e\u82b3", "\u7334\u7850", "\u4e09\u8c82\u5dba", "\u5927\u83ef", "\u5341\u5206", "\u671b\u53e4", "\u5dba\u8173", "\u5e73\u6eaa", "\u83c1\u6850"]
}

with open("f:/Antigravity/台鐵時刻表0701/test_enc.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

print("Wrote test_enc.json successfully!")
