"""
安全工具：密码哈希与校验
核心函数:
- hash_password: 把明文转换成不可逆的哈希值（存库用）
- verify_password: 登录时，把用户输入的明文合库里的哈希比对
使用 bcrypt 算法 - 它故意设计的“慢”，让暴力破解代价极高，是密码存储的行业标准
关键： 哈希是单向的，从哈希值无法还原出密码。所以就算数据库泄露，攻击者也拿不到用户的真实密码
"""
from passlib.context import CryptContext

# schemes 指定使用 bcrypt 算法， deprecated="auto" 让算法自动标记淘汰 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """把明文哈希化，注册时用"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码和哈希值是否匹配，登录时用，返回 True/False"""
    return pwd_context.verify(plain_password, hashed_password)