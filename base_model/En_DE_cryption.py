import json

from crypto.Cipher import AES

# accountInfo = "accountInfo_meter.json"
# with open(accountInfo, 'r') as load_f:
#     load_dict = json.load(load_f)
# info = load_dict
# host = info['host']  # 主机ip地址
# user = info['user']  # 用户名
# passwd = info['passwd']  # 密码
# db = info['db']  # 数据库名
# charset = info['charset']  # 字符集
# #print(host,'\n',user,'\n',passwd,'\n',db,'\n',charset)

from binascii import b2a_hex, a2b_hex

AES_LENGTH = 16

class prpcrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_ECB
        self.cryptor = AES.new(self.pad_key(self.key).encode(), self.mode)

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    # 加密内容需要长达16位字符，所以进行空格拼接
    def pad(self,text):
        while len(text) % AES_LENGTH != 0:
            text += ' '
        return text

    # 加密密钥需要长达16位字符，所以进行空格拼接
    def pad_key(self,key):
        while len(key) % AES_LENGTH != 0:
            key += ' '
        return key

    def encrypt(self, text):

        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        # 加密的字符需要转换为bytes
        # print(self.pad(text))
        self.ciphertext = self.cryptor.encrypt(self.pad(text).encode())
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

        # 解密后，去掉补足的空格用strip() 去掉

    def decrypt(self, text):
        plain_text = self.cryptor.decrypt(a2b_hex(text)).decode()
        return plain_text.rstrip(' ')


if __name__ == '__main__':
    pc = prpcrypt('Aslkfsjlsd5SA@#$%sd151dsf!')  # 初始化密钥
    # e = pc.encrypt(charset)
    # d = pc.decrypt(e)
    # print(e, d)
    e = pc.encrypt("emqx_yiwei")
    d = pc.decrypt(e)
    print(e, d)
