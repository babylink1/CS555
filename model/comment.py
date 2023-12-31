import pymysql
from config import Config

config = Config()

conn = pymysql.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD, db=config.DB_NAME,
                       cursorclass=pymysql.cursors.DictCursor)

cur = conn.cursor()

def add_comment(content, postId, author):
    sql = "INSERT INTO comment (content, postId, author) VALUES (%s, %s, %s)"
    conn.ping(reconnect=True)
    cur.execute(sql, (str(content), postId, author))
    conn.commit()

def get_comments_by_userId(userId):
    sql = "SELECT * FROM comment WHERE userId = %s"
    conn.ping(reconnect=True)
    cur.execute(sql, (userId,))
    result = cur.fetchall()
    if result:
        return result
    else:
        return []

def get_comments_by_postId(postId):
    sql = "SELECT * FROM comment WHERE postId = %s"
    conn.ping(reconnect=True)
    cur.execute(sql, (postId,))
    result = cur.fetchall()
    if result:
        return result
    else:
        return []

def delete_comment(id):
    sql = "DELETE FROM comment WHERE id = %s"
    conn.ping(reconnect=True)
    cur.execute(sql, (id))
    conn.commit()
    conn.close()
