import requests, time, json
import telegram
from bs4 import BeautifulSoup

class crawler():
	def __init__(self, webJson, telegramJson, wait_timeJson):
		self.info_telegram = self.ReadJsonFile(telegramJson)
		self.info_web = self.ReadJsonFile(webJson)
		self.waitTime = ReadTxtFile(wait_timeJson)
		self.botInfo = {'bot' : telegram.Bot(token = self.info_telegram['token']), 'chat_id' : self.info_telegram['chat_id']}
		self.price = None
		self.shippingCost = None

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

	# crawl_mallList 만들기
	def MakeMallList(self):
		while True:
			try:
				print('웹 사이트 접속을 시도중입니다...')
				response = requests.get(self.info_web['url'], headers = {'User-Agent': self.info_web['User-Agent']})

				soup = BeautifulSoup(response.text,'lxml')
				crawl_mallList = soup.select(self.info_web['selection_mallList'])
				return crawl_mallList

			except Exception as e:
				print('아래와 같은 오류가 발생했습니다.\n'  + str(e) + '\n' + '10초간 대기 후 다시 시도합니다.\n')
				time.sleep(10)
				continue

	# mallInfo 만들기
	def MakeMallInfo(self, crawl_mallList):
		mallList = []
		crawl_lowestMall = {}
		isEmpty = True

		for mall in crawl_mallList:
			self.price = mall.select_one(self.info_web['selection_price']).text
			self.shippingCost = mall.select_one(self.info_web['selection_shippingCost']).text[:-1]
			self.Digitize()
			href = mall.select_one(self.info_web['selection_href']).get('href')

			product = {'price' : self.price, 'shippingCost' : self.shippingCost, 'total' : self.price+self.shippingCost, 'href': href}
			mallList.append(product)

			if isEmpty == True:
				crawl_lowestMall = product
				isEmpty = False

			if product['total'] < crawl_lowestMall['total']:
				crawl_lowestMall = product

		info = {'mallList' : mallList, 'crawl_lowestMall' : crawl_lowestMall}
		return info

	# int형으로 변환
	def Digitize(self):
		self.price = self.price[:self.price.index(',')] + self.price[self.price.index(',')+1:]
		self.price = int(self.price)

		if (self.shippingCost == '무료배'):
			self.shippingCost = 0
		else:
			self.shippingCost = self.shippingCost[:self.shippingCost.index(',')] + self.shippingCost[self.shippingCost.index(',')+1:]
			self.shippingCost = int(self.shippingCost)

	# 알림
	def SendNoti(self, bool, crawl_lowestMall):
		if bool == True:
			self.botInfo['bot'].sendMessage(chat_id = self.botInfo['chat_id'], text = '최저가가 갱신되었습니다.\n' + '총 가격: ' + str(crawl_lowestMall['total']) + '\n' + '제품 가격: ' + str(crawl_lowestMall['price']) + '\n'+ '배송비: ' + str(crawl_lowestMall['shippingCost']) + '\n' + '사이트 주소: ' + str(crawl_lowestMall['href']))
		else:
			self.botInfo['bot'].sendMessage(chat_id = self.botInfo['chat_id'], text = '아쉽게도 최저가가 갱신되지 않았습니다.\n' + '현재 최저가: ' + str(crawl_lowestMall['total']) + '\n' +  '사이트 주소: ' + str(crawl_lowestMall['href']))


# txt 파일 읽기
def ReadTxtFile(fileName):
	try:
		with open(fileName, 'r', encoding = 'utf-8') as f:
			waitTime = int(f.read())
		return waitTime * 60
			
	except ValueError:
		print('    (WARNING) ' + str(fileName) + ' 파일을 불러올 수 없습니다. 숫자로만 쓰여있는 게 맞는지 확인해보세요.')
		return -1