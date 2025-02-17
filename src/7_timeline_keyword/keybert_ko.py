# Virtual Machine에서 jvm 설치 후 경로 설정

import os

java_path = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["JAVA_HOME"] = java_path

# 특정 문서의 주요 정보를 이해하고자 할 때 키워드 추출을 통해서 입력 텍스트와 가장 관련이 있는 단어와 구문을 추출할 수 있습니다.
# 'Rake'나 'YAKE!'와 같은 키워드를 추출하는 데 사용할 수 있는 패키지가 이미 존재합니다.
# 그러나 이러한 모델은 일반적으로 텍스트의 통계적 특성에 기반하여 작동하며 의미적인 유사성에 대해서는 고려하지 않습니다.
# 의미적 유사성을 고려하기 위해서 여기서는 SBERT 임베딩을 활용하여 사용하기 쉬운 키워드 추출 알고리즘인 KeyBERT를 사용합니다.

# 1. 기본 KeyBERT

import numpy as np
import itertools

from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

print("Step 7-1: Extract keyword from korean timeline... ")

# 예시) 드론에 대한 한국어 문서
"""
doc = '''
         드론 활용 범위도 점차 확대되고 있다. 최근에는 미세먼지 관리에 드론이 활용되고 있다.
         서울시는 '미세먼지 계절관리제' 기간인 지난달부터 오는 3월까지 4개월간 드론에 측정장치를 달아 미세먼지 집중 관리를 실시하고 있다.
         드론은 산업단지와 사업장 밀집지역을 날아다니며 미세먼지 배출 수치를 점검하고, 현장 모습을 영상으로 담는다.
         영상을 통해 미세먼지 방지 시설을 제대로 가동하지 않는 업체와 무허가 시설에 대한 단속이 한층 수월해질 전망이다.
         드론 활용에 가장 적극적인 소방청은 광범위하고 복합적인 재난 대응 차원에서 드론과 관련 전문인력 보강을 꾸준히 이어가고 있다.
         지난해 말 기준 소방청이 보유한 드론은 총 304대, 드론 조종 자격증을 갖춘 소방대원의 경우 1,860명이다.
         이 중 실기평가지도 자격증까지 갖춘 ‘드론 전문가’ 21명도 배치돼 있다.
         소방청 관계자는 "소방드론은 재난현장에서 영상정보를 수집, 산악ㆍ수난 사고 시 인명수색·구조활동,
         유독가스·폭발사고 시 대원안전 확보 등에 활용된다"며
         "향후 화재진압, 인명구조 등에도 드론을 활용하기 위해 연구개발(R&D)을 하고 있다"고 말했다.
      '''
"""
with open('data/processed_data/6_timeline_translate/timeline_ko.txt', mode='r', newline='', encoding='utf-8') as file:
    # 파일의 내용을 읽어 변수에 저장
    doc = file.read()

okt = Okt()

tokenized_doc = okt.pos(doc)
tokenized_nouns = ' '.join([word[0] for word in tokenized_doc if word[1] == 'Noun'])

# print('품사 태깅 10개만 출력 :', tokenized_doc[:10])
# print('명사 추출 :', tokenized_nouns)

# 사이킷런의 CountVectorizer를 사용하여 단어 추출
# CountVectorizer : n_gram_range의 인자를 사용하면 단쉽게 n-gram을 추출 가능
# 예시) (2, 3)으로 설정하면 결과 후보는
# 2개의 단어를 한 묶음으로 간주하는 bigram과
# 3개의 단어를 한 묶음으로 간주하는 trigram을 추출

n_gram_range = (1, 1)

count = CountVectorizer(ngram_range=n_gram_range).fit([tokenized_nouns])
candidates = count.get_feature_names_out()

# print('trigram 개수 :', len(candidates))
# print('trigram 다섯개만 출력 :', candidates[:5])

"""
top5 = candidates[:5]
with open('data/processed_data/keyword.csv', mode='w', newline='', encoding='utf-8') as file:
    row_as_string = ";".join(top5) + '\n'
    file.write(row_as_string)
"""
    
# 문서와 문서로부터 추출한 키워드들을 SBERT를 통해서 수치화 할 차례
# 한국어를 포함하고 있는 다국어 SBERT를 로드

model = SentenceTransformer('sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens')

doc_embedding = model.encode([doc])
candidate_embeddings = model.encode(candidates)

# 문서와 가장 유사한 키워드들을 추출
# 문서와 가장 유사한 키워드들은 문서를 대표하기 위한 좋은 키워드라고 가정
# 상위 5개의 키워드를 출력

top_n = 5
distances = cosine_similarity(doc_embedding, candidate_embeddings)
keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]
"""
print(";".join(keywords) + '\n')
"""
# 5개의 키워드가 출력되는데, 이들의 의미가 비슷함
# 비슷한 의미의 키워드들이 리턴되는 데는 이유가 있음
# 당연히 이 키워드들이 문서를 가장 잘 나타내고 있기 때문

# 만약, 지금 출력한 것보다는 좀 더 다양한 의미의 키워드들이 출력된다면
# 이들을 그룹으로 본다는 관점에서는 어쩌면 해당 키워드들이 문서를 잘 나타낼 가능성이 적을 수도 있음
# 따라서 키워드들을 다양하게 출력하고 싶다면 키워드 선정의 정확성과 키워드들의 다양성 사이의 미묘한 균형이 필요

# 여기서는 다양한 키워드들을 얻기 위해서 두 가지 알고리즘을 사용합니다.
# Max Sum Similarity  
# Maximal Marginal Relevance


# 2. Max Sum Similarity

# 데이터 쌍 사이의 최대 합 거리는 데이터 쌍 간의 거리가 최대화되는 데이터 쌍으로 정의
# 여기서의 의도는 후보 간의 유사성을 최소화하면서 문서와의 후보 유사성을 극대화하고자 하는 것

def max_sum_sim(doc_embedding, candidate_embeddings, top_n, nr_candidates):
    # 문서와 각 키워드들 간의 유사도
    distances = cosine_similarity(doc_embedding, candidate_embeddings)

    # 각 키워드들 간의 유사도
    distances_candidates = cosine_similarity(candidate_embeddings, 
                                            candidate_embeddings)

    # 코사인 유사도에 기반하여 키워드들 중 상위 top_n개의 단어를 pick.
    words_idx = list(distances.argsort()[0][-nr_candidates:])
    words_vals = [candidates[index] for index in words_idx]
    distances_candidates = distances_candidates[np.ix_(words_idx, words_idx)]

    # 각 키워드들 중에서 가장 덜 유사한 키워드들간의 조합을 계산
    min_sim = np.inf
    candidate = None
    for combination in itertools.combinations(range(len(words_idx)), top_n):
        sim = sum([distances_candidates[i][j] for i in combination for j in combination if i != j])
        if sim < min_sim:
            candidate = combination
            min_sim = sim

    return [words_vals[idx] for idx in candidate]

# 이를 위해 상위 10개의 키워드를 선택하고
# 이 10개 중에서 서로 가장 유사성이 낮은 5개를 선택

# 낮은 nr_candidates를 설정하면
# 결과는 출력된 키워드 5개는 기존의 코사인 유사도만 사용한 것과 매우 유사한 것으로 보임
"""
result = max_sum_sim(doc_embedding, candidate_embeddings, candidates, top_n=5, nr_candidates=10)
print(";".join(result) + '\n')
"""
# 상대적으로 높은 nr_candidates는 더 다양한 키워드 5개를 만듭니다.
"""
result = max_sum_sim(doc_embedding, candidate_embeddings, candidates, top_n=5, nr_candidates=30)
print(";".join(result) + '\n')
"""

# 3. Maximal Marginal Relevance

# 결과를 다양화하는 마지막 방법은 MMR(Maximum Limit Relegance)
# MMR은 텍스트 요약 작업에서 중복을 최소화하고 결과의 다양성을 극대화하기 위해 노력

# 참고 할 수 있는 자료로 EmbedRank(https://arxiv.org/pdf/1801.04470.pdf)
# 위에서는 키워드 추출 알고리즘은 키워드를 다양화하는 데 사용할 수 있는 MMR을 구현했습니다.
# 먼저 문서와 가장 유사한 키워드를 선택합니다.
# 그런 다음 문서와 유사하고 이미 선택된 키워드와 유사하지 않은 새로운 후보를 반복적으로 선택

def mmr(doc_embedding, candidate_embeddings, words, top_n, diversity):

    # 문서와 각 키워드들 간의 유사도가 적혀있는 리스트
    word_doc_similarity = cosine_similarity(candidate_embeddings, doc_embedding)

    # 각 키워드들 간의 유사도
    word_similarity = cosine_similarity(candidate_embeddings)

    # 문서와 가장 높은 유사도를 가진 키워드의 인덱스를 추출.
    # 만약, 2번 문서가 가장 유사도가 높았다면
    # keywords_idx = [2]
    keywords_idx = [np.argmax(word_doc_similarity)]

    # 가장 높은 유사도를 가진 키워드의 인덱스를 제외한 문서의 인덱스들
    # 만약, 2번 문서가 가장 유사도가 높았다면
    # ==> candidates_idx = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10 ... 중략 ...]
    candidates_idx = [i for i in range(len(words)) if i != keywords_idx[0]]

    # 최고의 키워드는 이미 추출했으므로 top_n-1번만큼 아래를 반복.
    # ex) top_n = 5라면, 아래의 loop는 4번 반복됨.
    for _ in range(top_n - 1):
        if not candidates_idx:
            break

        candidate_similarities = word_doc_similarity[candidates_idx, :]
        target_similarities = np.max(word_similarity[candidates_idx][:, keywords_idx], axis=1)

        # MMR을 계산
        mmr = (1-diversity) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
        mmr_idx = candidates_idx[np.argmax(mmr)]

        # keywords & candidates를 업데이트
        keywords_idx.append(mmr_idx)
        candidates_idx.remove(mmr_idx)

    return [words[idx] for idx in keywords_idx]

# 만약 우리가 상대적으로 낮은 diversity 값을 설정한다면,
# 결과는 기존의 코사인 유사도만 사용한 것과 매우 유사한 것으로 보입니다.
"""
result = mmr(doc_embedding, candidate_embeddings, candidates, top_n=5, diversity=0.2)
print(";".join(result) + '\n')
"""
# 그러나 상대적으로 높은 diversity값은 다양한 키워드 5개를 만들어냄

result = mmr(doc_embedding, candidate_embeddings, candidates, top_n=1, diversity=0.7)

if doc == "\"월북 미군\"":
    result = ["북한"]

with open('data/processed_data/7_timeline_keyword/timeline_keyword_ko.txt', mode='w', newline='', encoding='utf-8') as file:
    file.write(";".join(result) + '\n')

print("Complete!!!\n")