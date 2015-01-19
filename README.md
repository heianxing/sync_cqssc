### 重庆时时彩数据同步
- 从 http://chart.cp.360.cn/kaijiang/kaijiang?lotId=255401 同步数据

#### 依赖库
- requests (数据下载)
- MySQLdb
- torndb (数据写入 MySQL)

#### 使用方法
- 创建数据库表
    mysql -uuser -ppasswd < schema.sql

- 修改 sync_data.py 中的 DBHOST, SCHEMA, DBUSER, DBPASSWD 为实际数据，运行 python sync_data.py 即可
