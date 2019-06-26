import pandas as pd
import numpy as np
from konlpy.tag import Okt
import re
from string import ascii_letters
from gensim.models.doc2vec import Doc2Vec


class Preprocessor:
    okt = Okt()

    def speed_rate_function(self, offset_series, idx):
        # 전체 채팅 수
        length = offset_series.shape[0]

        # 전체 채팅 속도 (채팅 수 / 비디오 전체 시간)
        v = length / offset_series.iloc[-1]

        # 순간 채팅 속도(채팅 10개 / 채팅 10개가 올라오는 시)
        if idx < 5:
            dv = (idx + 5) / offset_series.iloc[idx + 4]
        elif length - idx <= 5:
            dv = (length - idx + 5) / (offset_series.iloc[-1] - offset_series.iloc[idx - 5])
        else:
            dv = 10 / (offset_series.iloc[idx + 5] - offset_series.iloc[idx - 5])

        return dv/v

    def tokenizer(self, line, remove_stopwords=False, stop_words=[]):
        # line: 전처리할 텍스트
        # okt: okt 객체를 반복적으로 생성하지 않고 미리 생성한 후 인자로 받는다.
        # remove_stopword: 불용어를 제거할지 여부 선택, 기본값은 False
        # stop_word: 불용어 사전은 사용자가 직접 입력해야 함. 기본값은 빈 리스트

        # okt 객체를 활용해 형태소 단위로 나눈다.
        word_token = self.okt.morphs(line, norm=True, stem=False)

        if remove_stopwords:
            # 불용어 제거(선택적)
            word_token = [token for token in word_token if not token in stop_words]

        return word_token

    def char_3x_shift(self, st):
        # 한글 자음 리스트
        CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        # 한글 모음 리스트
        JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ']
        # 알파벳 리스트
        ALPHABET_LIST = list(ascii_letters)
        # 구두기호 리스트 (\ 제외)
        PUNCTUATION_LIST = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':',
                            ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~']

        CHAR_LIST = [CHOSUNG_LIST, JUNGSUNG_LIST, ALPHABET_LIST]

        for l in CHAR_LIST:
            for c in l:
                st = re.sub(c + '{3,}', c * 3, st)

        for p in PUNCTUATION_LIST:
            st = re.sub('\\' + p + '{3,}', p * 3, st)

        return st

    def strip_e(self, st):
        RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
        return RE_EMOJI.sub(r'', st)

    def load_data(self, data_path, data_name):
        df = pd.read_csv(data_path+data_name)
        return df

    def doc2vec(self, d2v_file, df):
        d2v = Doc2Vec.load(d2v_file)
        # make test data set
        arr = np.zeros((df.shape[0], 151))
        for idx, item in enumerate(df['message']):
            arr[idx, :-1] = d2v.infer_vector(item)
            arr[idx, -1] = df.loc[idx, 'chat_speed']
        return arr

    def run(self, data_path, data_name, d2v_file):
        df = self.load_data(data_path, data_name)
        offset_series = df['offset_sec']
        for idx, item in enumerate(offset_series):
            df.loc[idx, 'chat_speed'] = self.speed_rate_function(offset_series, idx)
        tokenized_train_data = []
        df['message'] = df['message'].fillna('NaN')
        for idx, line in enumerate(df['message']):
            tokenized_train_data.append(self.tokenizer(self.strip_e(self.char_3x_shift(line))))
            if idx % 10000 == 0:
                print('{} / {}'.format(idx, df.shape[0]))
        df['message'] = tokenized_train_data
        arr = self.doc2vec(d2v_file, df)
        np.save(data_path+'ppd', arr)