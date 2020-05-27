import requests, time, json
from bs4 import BeautifulSoup

class crawler():
	# json 파일 읽기
	def ReadJsonFile(self, fileName):
		try:
			with open(fileName, 'r', encoding = 'utf-8') as f:
				contents = json.load(f)
			return contents

		except json.decoder.JSONDecodeError:
			print('    (WARNING) ' + str(fileName) + ' 파일을 읽을 수 없습니다. 형식이 잘못되지 않았는지 확인해보세요.')
			return -1
		
		except FileNotFoundError:
			print('    (WARNING) ' + str(fileName) + ' 파일을 찾을 수 없습니다. 경로를 올바르게 입력했는지 확인해보세요.')
			return -1

	# txt 파일 읽기
	def ReadTxtFile(self, fileName):
		try:
			with open(fileName, 'r', encoding = 'utf-8') as f:
				waitTime = int(f.read())
			return waitTime * 60
			
		except ValueError:
			print('    (WARNING) ' + str(fileName) + ' 파일을 불러올 수 없습니다. 숫자로만 쓰여있는 게 맞는지 확인해보세요.')
			return -1

	# crawl_mallList 만들기
	def MakeMallList(self, input_headers, url, selection):
		waitTime = 10
		while True:
			try:
				print('웹 사이트 접속을 시도중입니다...')
				response = requests.get(url, headers = input_headers)

				soup = BeautifulSoup(response.text,'lxml')
				crawl_mallList = soup.select(selection)
				return crawl_mallList

			except Exception as e:
				print('아래와 같은 오류가 발생했습니다.\n'  + str(e) + '\n' + str(waitTime) + '초간 대기 후 다시 시도합니다.\n')
				time.sleep(10)
				continue

	# int형으로 변환
	def Digitize(self, price, shippingCost):
		price = price[:price.index(',')] + price[price.index(',')+1:]
		price = int(price)

		if (shippingCost == '무료배'):
			shippingCost = 0
		else:
			shippingCost = shippingCost[:shippingCost.index(',')] + shippingCost[shippingCost.index(',')+1:]
			shippingCost = int(shippingCost)

		info = {'price' : price, 'shippingCost' : shippingCost}
		return info

	# mallInfo 만들기
	def MakeMallInfo(self, crawl_mallList, selection_price, selection_shippingCost, selection_href):
		mallList = []
		crawl_lowestMall = {}
		isEmpty = True

		for mall in crawl_mallList:
			before_price = mall.select_one(selection_price).text
			before_shippingCost = mall.select_one(selection_shippingCost).text[:-1]
			saleInfo = self.Digitize(before_price, before_shippingCost)
			price = saleInfo['price']
			shippingCost = saleInfo['shippingCost']
			href = mall.select_one(selection_href).get('href')

			product = {'price' : price, 'shippingCost' : shippingCost, 'total' : price+shippingCost, 'href': href}
			mallList.append(product)

			if isEmpty == True:
				crawl_lowestMall = product
				isEmpty = False

			if product['total'] < crawl_lowestMall['total']:
				crawl_lowestMall = product

		info = {'mallList' : mallList, 'crawl_lowestMall' : crawl_lowestMall}
		return info

	# 알림
	def SendNoti(self, bool, botInfo, crawl_lowestMall):
		if bool == True:
			botInfo['bot'].sendMessage(chat_id = botInfo['chat_id'], text = '최저가가 갱신되었습니다.\n' + '총 가격: ' + str(crawl_lowestMall['total']) + '\n' + '제품 가격: ' + str(crawl_lowestMall['price']) + '\n'+ '배송비: ' + str(crawl_lowestMall['shippingCost']) + '\n' + '사이트 주소: ' + str(crawl_lowestMall['href']))
		else:
			botInfo['bot'].sendMessage(chat_id = botInfo['chat_id'], text = '아쉽게도 최저가가 갱신되지 않았습니다.\n' + '현재 최저가: ' + str(crawl_lowestMall['total']) + '\n' +  '사이트 주소: ' + str(crawl_lowestMall['href']))
