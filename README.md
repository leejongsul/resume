# 경력
## [(주)유니토엔터테인먼트](http://unito-ent.com/)
* 기간: 13개월 (18.06.01 ~ 현재)
* 인원: 게임팀 3 ~ 4명

### [Elemental Guardians](https://play.google.com/store/apps/details?id=com.joywing.elga)
장르: 수집형 RPG

이전에 일본과 한국에서 오픈 이력이 있는 게임으로 입사 후 서버 프로그래머가 없는 상황에서 서버 인프라 구축을 하면서 게임을 개선 작업을 거쳐 2019.01.02 플레이스토어에 오픈했습니다.
이 후 라이브 서비스를 하면서 버그 수정과 기능 개선을 하였고, 신규 컨텐츠인 아레나(PVP)를 개발했습니다.

AWS EC2에 Kubernetes Cluster를 구성하여 서버를 운용하였고, 서버 어플리케이션에서 logstash 형식으로 로그를 출력하여 fluent-bit 에서 수집하여 elasticsearch에 저장하고 kibana에서 모니터링 하도록 구성했습니다.
내부 캐시로 사용하던 hazelcast를 Hibernate 2차 캐시와 분산 서버 캐시로 사용할 수 있도록 구성했습니다.

기술: java 8, spring boot, mariadb, hibernate, hazelcast, docker, aws, kubernetes, elasticsearch, kibana, jenkins
* Java
  * Spring boot 1.4.7
  * Hibernate 5.0.12
  * Hazelcast 3.11
  * Netty 4.1.3
* Firebase 
  * 인증(Auth)
  * 메세징(FCM)
* AWS
  * EC2
  * S3
  * Cloud front
  * Route 53
* Kubernetes
  * fluent-bit
  * elasticsearch
  * kibana

담당 업무
* 게임 서버
* 채팅 서버
* 운영 서버


## [(주)시그널앤코](http://signalnco.com/)
* 기간: 7개월 (17.08.08 ~ 18.03.12)
* 인원: 개발실 10명 + 기술개발 2명

스타트업으로 캐주얼한 게임(광고 수익)을 한달에 하나씩 런칭하는 것이 목표인 회사로 초기 게임은 서버 연동이 없었고 서버 직군이 제가 처음이라 초기 인프라 구축에 업무가 집중 되었습니다.

입사 후 PD와 논의하여 python을 사용하였고 언어에 익숙해지기 위해 회사 홈페이지 및 Press kit 페이지와 운영툴을 개발했으며
다음 게임에 들어가길 원하는 실시간 전투 시스템을 만들기 위한 R&D를 진행했습니다.

서버 배포는 작은 스튜디오라 대용량 서버가 필요없기에 [Rancher](https://rancher.com/)를 사용하여 Docker container로 배포 했습니다.

2017년 11월 개발실 PD 변경 및 조직 개편이 있었고 2017년 12월부터 2018년 3월까지 매치3 + 카지노 컨셉의 게임을 개발하다 집안 사정으로 퇴사했습니다.

### Z1
기간: 17.12 ~ 18.03

장르: 매치3 + 카지노

기술: python 2.7, flask, uwsgi, nginx, mysql, redis, mongodb, docker, linode
* 최초 python 3.6, aiohttp로 구성
* TD 합류 후 PHP, Codeigniter로 구성
* 기술개발실에서 서버팀장 합류 후 Python2.7, flask로 구성
 
담당 업무
* 등록, 로그인, 인증 API
* 프로필 변경 API
* 상점 기능 API
* HTTP2 R&D
 
![서버 구성](/images/z1.png)

### Oh! My Castle
기간: 2017.09 ~ 2017.10

장르: 클리커

기술: python3.6, aiohttp, gunicorn, nginx, mysql, redis, docker, linode

담당 업무
* 클라이언트 내 이벤트를 위해 시간 계산을 위한 Timestamp API
* IAP 검증(AOS, IOS) API
 
![서버 구성](/images/castle.png)

### Hompage
기간: 2017.08 ~ 2017.11

기술: python 3.6, aiohttp, gunicorn, nginx, mysql, redis, firebase, bigquery, docker, azure

담당 업무
* 회사 홈페이지 개발
* Press kit 페이지 개발
* Press kit 운영툴 개발
* Oh! My Castle 통계 view 개발
  
![서버 구성](/images/homepage.png)

## (주)와이피소프트 (폐업)
기간: 2016.09. ~ 2016.11.
메인 언어는 Java를 사용했고 서버 인력은 사수를 포함하여 2명이였습니다.
사수는 실시간 서버를 담당했고, 저는 전투(실시간)을 제외한 비동기로 처리할 수 있는 웹(API) 서버를 담당했습니다.

### Union
실시간 3D MMORPG 게임

java 8, spring 4, maven, hibernate, mysql

## [(주)티아이스퀘어](http://tisquare.com/)
기간: 2011.04.14 ~ 2016.01.13

메인 언어는 Java이며 초반엔 C++, C#도 사용했음.

### 겁나 많아서 나열해야함
