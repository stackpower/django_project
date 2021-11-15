from telethon.sync import TelegramClient
import sys


#time.sleep(3)
#ddd = client.iter_messages(channel_username, limit=10)
'''
aaa = client.get_messages(name2)
bbb = aaa[0].message
ccc = aaa[0].entities
ddd = aaa[0]._sender_id
'''
#channel_entity=client.get_entity(channel_username)
#posts = client(GetHistoryRequest(peer=channel_entity, limit=100, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
def scrap(path, user_id, ticker):
    news_list = []
    api_id = 1116717
    api_hash = '536480b495b2b6f2672079f3316ecaa2'
    phone = '+8562097394219'
    client = TelegramClient(phone, api_id, api_hash)

    client.connect()

    if not client.is_user_authorized():
        # client.sign_in(password="16797")
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))

    # channel_username='ef_ticker_bot' # your channel
    channel_username = 'earningsfly'  # your channel
    name2 = "ef_ticker_bot"
    client.send_message("ef_ticker_bot", "${}".format(ticker))
    while True:
        temp = client.get_messages(name2)
        if temp[0]._sender_id == 1078755645:
            first_name = temp[0]._sender.first_name
            msg = temp[0].message
            entity = temp[0].entities
            break
    msg_list = msg.split("\n")
    #print(msg_list[20])
    rating_target = entity[2].url
    trend = entity[3].url
    financial_chart = entity[4].url
    margin_chart = entity[5].url
    imcome_chart = entity[6].url
    for i in range(7, len(entity)):
        try:
            news_list.append(entity[i].url)
        except:
            pass
    #first_news = entity[24].url
    #second_news = entity[26].url
    #third_news = entity[28].url
    #fourth_news = entity[30].url
    first_news = news_list[0]
    second_news = news_list[1]
    third_news = news_list[2]
    fourth_news = news_list[3]
    #body = '<div class="row col-sm12"><div class="col-sm-5"><p class="m-0 m-b">{}</p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li></ul></div><div class="col-sm-7"><p class="m-0 m-b"></p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><div class="row"><a href="{}" target="_blank" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li></ul><img src="{}"></div></div>'.format(msg_list[0], rating_garget, msg_list[1], trend, msg_list[2], financial_chart, msg_list[3], margin_chart, msg_list[4], imcome_chart, msg_list[5], msg_list[6], msg_list[7], msg_list[8], msg_list[9], msg_list[10], msg_list[11], msg_list[12], msg_list[13], msg_list[14], msg_list[15], msg_list[16], first_news, msg_list[17].split(",")[0], msg_list[17].split(",")[1], second_news, msg_list[18].split(",")[0], msg_list[18].split(",")[1], third_news, msg_list[19].split(",")[0], msg_list[19].split(",")[1], fourth_news, msg_list[20].split(",")[0], msg_list[20].split(",")[1], rating_garget)
    #body = '<div class="row col-sm12"><div class="col-sm-6"><p class="m-0 m-b">{}</p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li><li class="list-group-item"><div class="block _500">{}</div></li></li><li class="list-group-item"><div class="block _500">{}</div></li></ul></div><div class="col-sm-6"><p class="m-0 m-b">{}</p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><div class="row"><a href="{}" target="_blank" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li></ul><img src="{}"></div></div>'.format(
    #    msg_list[0], rating_target, msg_list[1], trend, msg_list[2], financial_chart, msg_list[3], margin_chart, msg_list[4], imcome_chart, msg_list[5], msg_list[6], msg_list[7], msg_list[8], msg_list[9], msg_list[10], msg_list[11], msg_list[12], msg_list[13], msg_list[14], msg_list[15], msg_list[16], first_news, msg_list[17][: msg_list[17].rfind(",")], msg_list[17][msg_list[17].rfind(",")+1:], second_news, msg_list[18][:msg_list[18].rfind(",")], msg_list[18][msg_list[18].rfind(",")+1:], third_news, msg_list[19][:msg_list[19].rfind(",")],
    #    msg_list[19][msg_list[19].rfind(",")+1:], fourth_news, msg_list[20][:msg_list[20].rfind(",")], msg_list[20][msg_list[20].rfind(",")+1:], rating_target)
    img_content = '<div class="row col-sm12"><div class="col-sm-5"><p class="m-0 m-b">{}</p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li><li class="list-group-item"><a href="{}" target="_blank" class="block _500 text-info">{}</a></li>'.format(msg_list[0], rating_target, msg_list[1], trend, msg_list[2], financial_chart, msg_list[3], margin_chart, msg_list[4], imcome_chart, msg_list[5])
    link_content = '</ul></div><div class="col-sm-7"><p class="m-0 m-b">{}</p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><div class="row"><a href="{}" target="_blank" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li></ul><img src="{}"></div></div>'.format(msg_list[-5], first_news, msg_list[-4][: msg_list[-4].rfind(",")], msg_list[-4][msg_list[-4].rfind(",") + 1:], second_news, msg_list[-3][:msg_list[-3].rfind(",")], msg_list[-3][msg_list[-3].rfind(",") + 1:], third_news, msg_list[-2][:msg_list[-2].rfind(",")], msg_list[-2][msg_list[-2].rfind(",") + 1:], fourth_news, msg_list[-1][:msg_list[-1].rfind(",")], msg_list[-1][msg_list[-1].rfind(",") + 1:], rating_target)
    text_content = ""
    for i in range(6, len(msg_list)-5):
        text_content += '<li class="list-group-item"><div class="block _500">{}</div></li>'.format(msg_list[i])


    #link_content = '</ul></div><div class="col-sm-6"><p class="m-0 m-b">{}</p><ul class="list-group m-b" ui-jp="sortable"><li class="list-group-item"><div class="row"><a href="{}" target="_blank" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li><li class="list-group-item"><div class="row"><a href="{}" target="_blank" class="block _500"><p class="text-primary">{}</p></a><p class="block _500">{}</p></div></li></ul><img src="{}"></div></div>'.format(msg_list[-5], first_news, msg_list[-4][: msg_list[-4].rfind(",")], msg_list[-4][msg_list[-4].rfind(",")+1:], second_news, msg_list[-3][:msg_list[-3].rfind(",")], msg_list[-3][msg_list[-3].rfind(",")+1:], third_news, msg_list[-2][:msg_list[-2].rfind(","), msg_list[-2][msg_list[-2].rfind(",")+1:], fourth_news, msg_list[-1][:msg_list[-1].rfind(",")], msg_list[-1][msg_list[-1].rfind(",")+1:], rating_target)
    body = img_content + text_content + link_content
    #print(body)
    f = open("{}//earningsfly//{}.txt".format(path, user_id), "w")
    #f = open("earningsfly//{}.txt".format(user_id), "w")
    f.write(body)
    f.close()

if __name__ == "__main__":
    path = sys.argv[1]
    user_id = sys.argv[2]
    ticker = sys.argv[3]
    scrap(path, user_id, ticker)
    #scrap("", 1, "ADM")

pass











