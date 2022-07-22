import requests, json
msgUnicode = 'E'
msgRecipient = '966555620127'
msgSender = 'NOQUA-IT'
msgText = "There are several serious NWP alerts. Urgent action is required to avoid loss of fish"
userName = 'robian'
userPW = 'robian'

URL = "http://sms.malath.net.sa/httpSmsProvider.aspx"
payload = "?username=" + userName
payload += "&password=" + userPW
payload += "&mobile=" + msgRecipient
payload += "&unicode=" + msgUnicode
payload += "&message=" + msgText
payload += "&sender=" + msgSender

response = requests.get(URL+payload, timeout=13)
print(URL+payload)
# print(response.text)
print("Return code from maladh = {}".format(response.status_code))

# if __name__ == '__main__':
#     main()
# http://sms.malath.net.sa/httpSmsProvider.aspx?username=robian&password=robian&mobile=966555620127&unicode=E&message=Testing&sender=NOQUA-IT