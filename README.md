<!-- <h1> 
  서울시 상권별 외식업 분포 및 매출 특성 분석
  <h3>
    매출-유동인구-소득의 상관관계 규명 및 성장•진입 전략 제안
  </h3>
</h1> -->

<h1 align="center"><strong>서울시 상권별 외식업 분포 및 매출 특성 분석</strong></h1>
<p align="center"><strong>매출-유동인구-소득의 상관관계 규명 및 성장•진입 전략 제안</strong></p>

<a href=https://eda-repo-4-hp2bzipnzdbrre9jaeznnw.streamlit.app/>
<img width="1200" height="630" alt="서울시 상권분석 대시보드 스크린샷" src="https://github.com/user-attachments/assets/230310af-45e1-488d-a16a-95c1eb205c8e" />
</a>

<p align="center">
  <b>4조 InsighTrio</b>
</p>

<div align="center">

  | Name | Role | GitHub | Email |
  |------|------|---------|--------|
  | 이가람 | 팀장, 데이터 분석, DB 설계, 대시보드 구현 | [@rraamm8](https://github.com/rraamm8) | garam.rachel.lee@gmail.com |
  | 이충협 | 데이터 분석, 특화상권 분석, 기술조사 및 문서화 | [@chunghyeop](https://github.com/jihunlee) | leech3583@gmail.com |
  | 양효인 | 데이터 분석, DB 설계, 대시보드 구현 및 배포 | [@hyoinyang](https://github.com/hyoinyang) | hyoinyang02@gmail.com |
  
</div>
<br><br>

## 데이터 개요

### 활용 데이터

서울시 열린데이터 광장 공공데이터의 2024년 분기별 상권별/업종별 매출 데이터, 점포 수, 유동/상주/직장 인구, 2024년 행정동별 소득 소비 데이터 활용

* 상권 기본정보

  * 영역-상권 (상권 소속 행정구역 및 면적정보) 서울시 상권분석서비스([영역-상권](https://data.seoul.go.kr/dataList/OA-15560/S/1/datasetView.do)) 
  * 점포-상권 (점포수, 유사업종점포수, 개폐업율) 서울시 상권분석서비스([점포-상권](https://data.seoul.go.kr/dataList/OA-15577/S/1/datasetView.do))

* 추정매출

  * 추정매출-상권 (24년 시간대별/요일별/연령별 매출) 서울시 상권분석서비스([추정매출-상권](https://data.seoul.go.kr/dataList/OA-15572/S/1/datasetView.do#)) 

* 유동인구 데이터

  * 길단위인구-상권 (상권별 시간대별/요일별 유동인구) 서울시 상권분석서비스([길단위인구-상권](https://data.seoul.go.kr/dataList/OA-15568/S/1/datasetView.do)) 
  * 상주인구-상권 (성별, 연령대별) 서울시 상권분석서비스([상주인구-상권](https://data.seoul.go.kr/dataList/OA-15584/S/1/datasetView.do)) 
  * 직장인구-상권 (성별, 연령대별) 서울시 상권분석서비스([직장인구-상권](https://data.seoul.go.kr/dataList/OA-15569/S/1/datasetView.do)) 

* 월평균소득(구매력데이터)

  * 소득소비 - 행정동 서울시 상권분석서비스 ([소득소비-행정동](https://data.seoul.go.kr/dataList/OA-22166/S/1/datasetView.do)) 
  * (상권 및 상권배후지는 소득데이터 수집하기에 면적이 너무 작아서 19년 이후 업데이트 중지되었기에, 최근데이터까지 업데이트되어 있고 잠재적 소비자가 있는 행정동단위로 확대하여 소득소비 지표 판단)
<br>
<br>

### 용어 정의

* 상권(1650개): 골목상권, 발달상권, 전통시장 상권, 관광특구 상권 4개 분류

* 골목상권(1090개): 대로변이 아닌 거주지 안의 좁은 도로를 따라 형성되는 상업 세력의 범위
  1. 도로길이 400M 이상인 길을 추출하고
  2. 도로 네트워크를 통해 길의 중심점으로부터 200M 반경까지 길단위 영역 생성
  3. 길단위 영역중에 점포수가 30개이상 골목상권 영역 추출

* 발달상권(249개): 8개 업종대분류 점포가 밀집한 지구. 유통산업발전법 제5조의 법조항에 따라 2천 제곱미터 이내 50개 이상의 상점이 분포하는 경우 “상점가”라 하고, 배후지를 고려하지 않은 도보이동이 가능한 범위내의 상가업소밀집지역을 발달상권으로 정의

* 전통시장 상권(305개): 오랜 기간에 걸쳐 일정한 지역에서 자연발생적으로 형성된 상설시장이나 정기시장

* 관광특구 상권(6개): 관광활동이 주로 이루어지는 지역적 공간

* 외식업 업종 분류 10종 (서울시, 통계청 선정): 한식음식점, 중식음식점, 일식음식점, 양식음식점, 제과점, 패스트푸드점, 치킨전문점, 분식전문점, 호프-간이주점, 커피-음료

<br>
<br>

## 데이터 설계 (ERD)
<img width="1918" height="1298" alt="image" src="https://github.com/user-attachments/assets/c36ae517-4977-4c15-92fa-20f29fec1619" />



<br>
<br>

## 가설 설정

Q1: 상권 면적 대비 점포 밀도와 매출 규모의 관계는 업종별로 어떻게 다른가? 

가설: 매출이 높을 수록 점포 밀도가 높을 것이다.

Q2: 주중/주말별 유동인구가 업종별 매출에 미치는 영향은?

가설: 주말 유동인구 강세 지역의 경우 “호프-간이주점”, “커피-음료” 업종이 상대적으로 강세 경향을 보일 것이다.

Q3: 상주/직장 인구 특성(성별/연령)과 업종별 매출 성과의 상호작용은?

가설: 직장 인구 비중이 높은 지역의 매출은 주중 점심시간대에 집중적으로 분포할 것이다. 상주 인구 비중이 높은 지역의 매출은 요일별/시간대별로 고루 분포할 것이다.

Q4: 행정동 소득/소비 지표가 배후 수요(구매력)로서 매출을 어느 정도 설명하는가?

가설: 소득 수준이 높은 행정동의 상권의 매출이 높을 것이다. 

Q5: 개폐업율이 매출에 미치는 영향은?

가설: 개업율이 높은 상권의 매출이 높고, 폐업율이 높은 경우 매출이 낮을 것이다.
<br>
<br>

## 데이터 분석



<br>
<br>

## 개선 및 확장 방향







Thanks to [JetBrains](https://www.jetbrains.com) for supporting us with a [free Open Source License](https://www.jetbrains.com/buy/opensource).


