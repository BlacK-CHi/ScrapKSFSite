'''
코리아스타트업포럼 회원사 세부 페이지 크롤링 코드

작성환경 : Lubuntu 5.19.0-32-generic x86_64 + Google Colaboratory
테스트 환경 : Google Colaboratory

'''

import json
import pandas as pd #데이터 미리보기 및 후가공을 위한 pandas 라이브러리 활용
import requests
import warnings
import os

warnings.filterwarnings("ignore") #requests에서 https 없이 사용할 경우 경고문이 뜨는데, 이 경고문을 표시하지 않도록 함.


company_list= [] #크롤링한 데이터를 입력할 리스트 (임시 리스트)


#requests.get() 실행 시 사용할 응답 헤더(Request Header)
dummy_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36', #브라우저 정보
    'Host': 'api.kstartupforum.org', #호스트 정보
    'Sec-Fetch-Dest': 'document'
    }

#--------------------------------- 함수 : 분야 크롤링 --------------------------------------#

def FieldCompositor(data):
  temp = '' #함수를 호출할 때마다 임시변수인 temp는 비운다 (쓰레기값 방지)
  for i in range(0, 100):
    try:
      temp = temp + data['data']['businessList'][i]['flagName'] + ',' #분야명을 temp에 추가하고, 분야가 여러 개일 경우 구분을 위해 반점을 추가한다.
    except IndexError: #index값이 초과되어 오류가 날 경우, 예외처리. 
      continue
  
  temp = temp.rstrip(',') #끝의 불필요한 반점을 삭제한다.
  return temp #조합이 끝난 분야 문자열을 반환한다.

#--------------------------------- 데이터 크롤링 진행 --------------------------------------#

startpage = int(input('시작 지점 >> ')) #크롤링 시작 지점 페이지를 입력받음
endpage = int(input('종료 지점 >> ')) #크롤링 끝 지점 페이지를 입력받음

#크롤링 진행 반복문 - endpage 값에 도달할 때까지 크롤링을 진행함.
for page in range(startpage, endpage):
  try : 
    req = requests.get(f'https://api.kstartupforum.org/user/{page}', headers=dummy_headers, verify=False) #SSL 오류를 방지하기 위해 인증서 확인을 비활성화하고, 응답 헤더를 지정한다.
    data = req.json() #받아온 데이터를 JSON의 형태로 변환한다.

    company_list.append( #받아온 JSON의 KEY값을 기준으로, 자료를 임시 리스트에 저장한다.
      {
        "name" : data['data']['companyNameKo'], #한글명칭
        "location" : data['data']['baseAddress'] + ' ' + data['data']['detailAddress'], #기본주소 + 세부주소를 합쳐 하나의 주소로 출력함
        "introduce" : data['data']['introduce'], #기업 소개
        "field" : FieldCompositor(data), #위의 분야 크롤링 함수 참조
        "pagenumber" : page #홈페이지 내에서 사용되는 개별 페이지 번호, 필요없으면 삭제해도 무방.
      }
      
  )
    os.system('cls')
    print(f'[수집] {page}/{endpage}번째 페이지 처리 중....') #현재 크롤링 중인 페이지의 index 번호 출력
  
  except KeyError: #아무것도 없는 더미페이지의 경우 Key값이 아예 달라(error 키값 발생) 오류가 발생하는데, 이 경우 예외처리 후 다시 크롤링을 진행함. 이 방법으로 빈 페이지를 건너뜀.
    continue

#크롤링이 끝나면 company_list 리스트의 내용을 임의의 JSON 파일에 기록한다.
with open(f"{startpage}-{page}_scraping_result.json", "w") as outfile:
  print('[파일] JSON 파일로 기록 중 ...') #처리 중 메시지.
  json.dump(company_list, outfile, indent=4, ensure_ascii=False) #ensure_ascii 옵션이 없을 경우 한글이 깨져 표시되니 주의 바람!




#--------------------------------- pandas를 활용하여 데이터 후가공 --------------------------------------#

with open(f"{startpage}-{page}_scraping_result.json") as dfinput:
  js = json.loads(dfinput.read())

df = pd.DataFrame(js) #데이터프레임 형식으로 데이터를 변환한다. 시각적으로 확인하고 싶은 경우 아래 줄의 주석을 해제한다. (Colab/Jupyter Notebook 환경에서만 동작. 아마도?)
print('[파일] CSV / 엑셀 파일로 처리 중 ...') #처리 중 메시지.
#df
df.to_csv(f"{startpage}-{page}_scraping_result.csv", index = False) #데이터프레임 형식의 데이터를 CSV 파일(엑셀에서 인식 가능)로 출력한다.

print('[완료] 작업이 끝났습니다. 파일을 확인해 주세요.') #작업 완료 메시지. 
print(f'[알림] 마지막으로 처리된 페이지 번호는 {page}입니다. 다음 크롤링 때에는 {page+1}번부터 시작해주세요.')