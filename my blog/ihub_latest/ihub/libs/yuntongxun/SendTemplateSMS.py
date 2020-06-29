from ihub.libs.yuntongxun.CCPRestSDK import REST

# ���ʺ�
accountSid = '8aaf07086eb122c3016ecb93d6820e74'

# ���ʺ�Token
accountToken = 'dfd8f1a5818146169ee717cad1e25f54'

# Ӧ��Id
appId = '8aaf07086eb122c3016ecb93d6e40e7b'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'


# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ�б� ���磺['12','34']���粻���滻���� ''
# @param $tempId ģ��Id

class CCP():
    '''�Լ���װ�ķ��Ͷ��ŵĸ�����'''
    instance = True

    def __new__(cls):
        # �ж�cpp����û���Ѿ������õĶ������û������һ�������ұ���
        # ����� ������Ķ���ֱ�ӷ���
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)
            # ��ʼ�� REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.instance = obj
        return cls.instance

    def sendTemplateSMS(self, to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))
        #smsMessafeSid:xxxxxx
        #dateCreated:xxxxxx
        #statusCode:000000
        status_code=result.get('statusCode')
        if status_code =='000000':
            return 0 #���ͳɹ�
        else:
            return -1 #����ʧ��



if __name__ == '__main__':
    ccp = CCP()
    # 000000 �ɹ�
    ccp.sendTemplateSMS("15988046655", ['1234', '5'], 1)
