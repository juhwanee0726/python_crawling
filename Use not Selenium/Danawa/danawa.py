import telegram, json, time, sys
from datetime import datetime
import source as src

func = src.crawler()

try:
	# 사전 준비
	print('telegram.json과 web.json을 읽습니다...')
	info_telegram = func.ReadJsonFile('info/telegram.json')
	info_web = func.ReadJsonFile('info/web.json')

	print('waitTime.txt를 읽습니다...')
	waitTime = func.ReadTxtFile('info/wait_time.txt')
	if (info_telegram == -1 or info_web== -1 or waitTime == -1):
		raise NotImplementedError

	print('텔레그램 봇을 설정하는 중입니다...')
	botInfo = {'bot' : telegram.Bot(token = info_telegram['token']), 'chat_id' : info_telegram['chat_id']}

	# 본 작업 시작
	while True:
		print('\n[' + str(datetime.now()) + ']')

		print('lowest_mall.json을 읽습니다...')
		json_lowestMall = func.ReadJsonFile('lowest_mall.json')
		if (json_lowestMall == -1):
			raise NotImplementedError

		# 변수 생성
		crawl_mallList = func.MakeMallList({'User-Agent': info_web['User-Agent']}, info_web['url'], info_web['selection_mallList'])
		mallInfo = func.MakeMallInfo(crawl_mallList, info_web['selection_price'], info_web['selection_shippingCost'], info_web['selection_href'])
		crawl_lowestMall = mallInfo['crawl_lowestMall']
		mallList = mallInfo['mallList']

		# 최저가 갱신 + 알림
		print('최저가가 갱신되었는지 확인합니다...')
		print('\t몰 최저가:' , crawl_lowestMall['total'])
		print('\tjson 최저가:', json_lowestMall['total'])
		
		if (crawl_lowestMall['total'] < json_lowestMall['total'] or json_lowestMall['href'] == "first time"):
			with open('lowest_mall.json', 'w') as f:
				json.dump(crawl_lowestMall, f, indent = 4)
			func.SendNoti(True, botInfo, crawl_lowestMall)
			print('(!)최저가가 갱신되었습니다! 봇 알림을 확인해보세요.')
		else:
			print('아쉽게도 최저가가 갱신되지 않았습니다.')

		# 가격 리스트를 json형식으로 저장
		print('가격 리스트를 저장합니다.')
		with open('mall_list.json', 'w') as json_file:
			json.dump(mallList, json_file, indent = 4)
		
		# waitTime만큼 대기
		print(str(int(waitTime/60)) + '분 동안 기다립니다...\n')
		time.sleep(waitTime)

except NotImplementedError:
	sys.exit()

except Exception as e:
	print('아래와 같은 오류가 발생했습니다.\n' + str(e))
	botInfo['bot'].sendMessage(chat_id = botInfo['chat_id'], text = '아래와 같은 오류가 발생했습니다.\n' + str(e))

