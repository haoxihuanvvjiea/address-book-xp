# 通讯录管理系统（XP结对项目）
## 项目简介
本项目是前后端分离的通讯录管理系统，后端采用FastAPI，前端使用原生HTML，基于SQLite数据库存储数据。支持联系人管理、多联系方式维护、收藏功能以及Excel导入导出。
结对分工：
- 后端：main.py，负责接口编写、数据库业务逻辑实现
- 前端：index.html，负责页面展示、用户交互、调用后端接口

## 运行环境
Python >= 3.8
依赖包：fastapi、uvicorn、openpyxl

安装依赖命令：
```bash
pip install fastapi uvicorn openpyxl
```

## 启动步骤
1. 将 main.py、index.html 放在同一个文件夹
2. 在该文件夹打开终端执行：
```bash
uvicorn main:app --reload
```
3. 访问地址
- 通讯录页面：[http://127.0.0.1:8000](http://127.0.0.1:8000)
- 自动接口文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 功能清单
1. 联系人：新增、查看全部、删除、切换收藏状态
2. 联系方式：为联系人添加多条联系方式、单独删除某一条联系方式
3. Excel功能：导出全部联系人信息、上传Excel批量导入联系人

## 接口列表
| 请求方法 | 接口地址 | 功能说明 |
| ---- | ---- | ---- |
| POST | /api/contact | 新增联系人 |
| GET | /api/contact | 查询全部联系人 |
| DELETE | /api/contact/{id} | 删除联系人 |
| PUT | /api/contact/{id} | 修改联系人收藏状态 |
| POST | /api/contact/{cid}/method | 添加联系方式 |
| DELETE | /api/method/{mid} | 删除单条联系方式 |
| GET | /api/excel/export | 导出Excel |
| POST | /api/excel/import | 导入Excel |

## 迭代记录
迭代1：提交 main.py，完成后端接口与SQLite数据库逻辑
迭代2：提交 index.html，完成前端页面，对接后端接口
迭代3：提交 README.md，补充项目说明文档，前后端联调完成