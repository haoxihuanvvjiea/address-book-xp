from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
import sqlite3
import io
from openpyxl import Workbook, load_workbook

app = FastAPI(title="通讯录XP作业")
DB_FILE = "address.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # 联系人主表
    cur.execute('''
    CREATE TABLE IF NOT EXISTS contact (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        is_bookmark INTEGER DEFAULT 0
    )
    ''')
    # 联系方式子表 一对多
    cur.execute('''
    CREATE TABLE IF NOT EXISTS contact_method (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        method_type TEXT,
        content TEXT,
        FOREIGN KEY (contact_id) REFERENCES contact(id) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# 主页返回html
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 新增联系人
@app.post("/api/contact")
async def add_contact(name: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO contact (name,is_bookmark) VALUES (?,0)", (name,))
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": cid, "name": name, "is_bookmark":0}

# 获取所有联系人（带联系方式）
@app.get("/api/contact")
async def get_all():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    contacts = cur.execute("SELECT * FROM contact").fetchall()
    res = []
    for c in contacts:
        methods = cur.execute("SELECT * FROM contact_method WHERE contact_id=?", (c["id"],)).fetchall()
        res.append({
            "id": c["id"],
            "name": c["name"],
            "is_bookmark": c["is_bookmark"],
            "methods": [{"id":m["id"], "type":m["method_type"], "content":m["content"]} for m in methods]
        })
    conn.close()
    return res

# 切换收藏
@app.put("/api/contact/{cid}/bookmark")
async def toggle_bookmark(cid:int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT is_bookmark FROM contact WHERE id=?", (cid,))
    row = cur.fetchone()
    if not row:
        return {"msg":"不存在"}
    new_val = 1 - row[0]
    cur.execute("UPDATE contact SET is_bookmark=? WHERE id=?", (new_val, cid))
    conn.commit()
    conn.close()
    return {"ok":True, "is_bookmark":new_val}

# 删除联系人
@app.delete("/api/contact/{cid}")
async def del_contact(cid:int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM contact WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    return {"ok":True}

# 添加联系方式
@app.post("/api/contact/{cid}/method")
async def add_method(cid:int, method_type:str, content:str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO contact_method(contact_id,method_type,content) VALUES (?,?,?)", (cid,method_type,content))
    mid = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id":mid}

# 删除联系方式
@app.delete("/api/method/{mid}")
async def del_method(mid:int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM contact_method WHERE id=?", (mid,))
    conn.commit()
    conn.close()
    return {"ok":True}

# 导出Excel
@app.get("/api/excel/export")
async def export_excel():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    contacts = cur.execute("SELECT * FROM contact").fetchall()
    wb = Workbook()
    ws = wb.active
    ws.title = "通讯录"
    ws.append(["联系人ID","姓名","是否收藏","联系方式类型","联系方式内容"])
    for c in contacts:
        methods = cur.execute("SELECT * FROM contact_method WHERE contact_id=?", (c["id"],)).fetchall()
        if len(methods)==0:
            ws.append([c["id"], c["name"], "⭐" if c["is_bookmark"] else ""])
        else:
            for m in methods:
                ws.append([c["id"], c["name"], "⭐" if c["is_bookmark"] else "", m["method_type"], m["content"]])
    conn.close()
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment;filename="address_book.xlsx"'}
    )

# 导入Excel
@app.post("/api/excel/import")
async def import_excel(file:UploadFile=File(...)):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    content = await file.read()
    wb = load_workbook(io.BytesIO(content))
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    # 跳过表头
    for r in rows[1:]:
        if not r[1]:
            continue
        name = r[1]
        is_mark = 1 if r[2] == "⭐" else 0
        # 先看这个名字是否存在，简单处理：新增
        cur.execute("INSERT INTO contact(name,is_bookmark) VALUES (?,?)", (name,is_mark))
        new_cid = cur.lastrowid
        if len(r)>=5 and r[3] and r[4]:
            cur.execute("INSERT INTO contact_method(contact_id,method_type,content) VALUES (?,?,?)", (new_cid, r[3], r[4]))
    conn.commit()
    conn.close()
    return {"ok":True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
