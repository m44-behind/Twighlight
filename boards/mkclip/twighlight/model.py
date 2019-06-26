import numpy as np
import pandas as pd
from keras.models import load_model as lm


class Analyser:
    def load_data(self, data_file):
        return np.load(data_file)

    # 데이터셋 생성 함수
    def seq2dataset(self, dataset, window_size=5):
        preprocessed_dataset = []
        for i in range(dataset.shape[0] - window_size):
            subset = dataset[i:i + window_size, :]
            preprocessed_dataset.append(subset)
        return np.array(preprocessed_dataset)

    # 모델 로딩 함수
    def load_model(self, model_file):
        return lm(model_file)

    # 분석 함수
    def analyse(self, model, dataset):
        size = dataset.shape[0]
        return model.predict(dataset[:-(size%10000)], batch_size=10000)

    # 전체 실행 함수
    def run(self, data_file, model_file):
        dataset = self.load_data(data_file)
        preprocessed_dataset = self.seq2dataset(dataset)
        model = self.load_model(model_file)
        return self.analyse(model, preprocessed_dataset)


class ClipMaker:
    # 결과 np.array 를 df로 출력
    def convert_result_to_dataframe(self, result, clip_value=0.025):
        df = pd.DataFrame(result.reshape(result.shape[0]), columns={'clip_value'})
        df['clip'] = df['clip_value'] > clip_value
        return df

    # 클립 시작 부분의 index 리스트 출력
    def get_clip_indexes(self, dataframe, continuous_count=30):
        clip_df = dataframe.loc[dataframe['clip'] == True]
        indexes = list(clip_df.index)
        indexes.reverse()
        prev = 0
        count = 0
        clip_indexes = []
        for idx in indexes:
            if idx == prev - 1:
                count = count + 1
            else:
                if count >= continuous_count:
                    clip_indexes.append(prev)
                    count = 0
            prev = idx
        clip_indexes.reverse()
        return clip_indexes

    def run(self, result, chat_file):
        chat = pd.read_csv(chat_file)
        df = self.convert_result_to_dataframe(result)
        clip_indexes = self.get_clip_indexes(df)
        return chat.loc[clip_indexes]['offset_sec']
