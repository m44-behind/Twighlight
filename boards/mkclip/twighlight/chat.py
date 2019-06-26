# video 원본 채팅 받는 함수
import json
import urllib.request
import re
import pandas as pd
from datetime import datetime
from datetime import timedelta
from decouple import config

class Collector:
    # emoji 제거 함수
    def strip_e(self, st):
        RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
        return RE_EMOJI.sub(r'', st)


    def get_video_comments(self, apikey, video_id, file):
        url = f"https://api.twitch.tv/helix/videos?id={str(video_id)}"
        req = urllib.request.Request(url, headers={"Client-ID": apikey})
        u = urllib.request.urlopen(req)
        c = u.read().decode('utf-8')
        js = json.loads(c)
        duration = js['data'][0]['duration']

        # duration 형식 변경
        if duration.find('s') != -1:
            duration = duration.replace('s', '')
        if duration.find('m') != -1:
            temp = duration.split('m')
            if temp[0].find('h') != -1:
                temp2 = temp[0].split('h')
            else:
                temp2 = [0, temp[0]]
            duration = int(temp2[0]) * 60 ** 2 + int(temp2[1]) * 60 + int(temp[1])

        # chat 가져오기
        cursor = ''
        count = 0
        msg_idx = 0
        while (1):
            try:
                url = ''
                if count == 0:
                    url = 'https://api.twitch.tv/kraken/videos/' + str(video_id) + '/comments'
                else:
                    url = 'https://api.twitch.tv/kraken/videos/' + str(video_id) + '/comments?cursor=' + str(cursor)
                req = urllib.request.Request(url, headers={"Client-ID": apikey,
                                                           "Accept": "application/vnd.twitchtv.v5+json"})
                u = urllib.request.urlopen(req)
                c = u.read().decode('utf-8')
                js = json.loads(c)
                endCount = 0
                try:
                    for number, com in enumerate(js['comments']):
                        dateString = js['comments'][number]['created_at']
                        if '.' in dateString:
                            dateString = re.sub(r".[0-9]+Z", "Z", dateString)
                        date = datetime.strptime(dateString, "%Y-%m-%dT%H:%M:%SZ")

                        if int(duration) < int(js['comments'][number]['content_offset_seconds']):
                            endCount = 1
                            break
                        else:
                            created_at = str(date + timedelta(hours=9))
                            # chat_df 생성
                            chat_df = pd.DataFrame([[str(js['comments'][number]['_id']),
                                                     str(js['comments'][number]['content_id']),
                                                     str(js['comments'][number]['commenter']['name']),
                                                     str(date),
                                                     str(js['comments'][number]['content_offset_seconds']),
                                                     msg_idx,
                                                     self.strip_e(str(js['comments'][number]['message']['body']))
                                                     ]],
                                                   columns=['chat_id', 'video_id', 'user_id', 'created_at',
                                                            'offset_sec', 'message_idx', 'message'])

                            # 처리된 row csv로 저장
                            chat_df.to_csv(file,
                                           header=False,
                                           index_label=False,
                                           index=False,
                                           encoding='utf-8')

                            msg_idx = msg_idx + 1

                except Exception as e:
                    print(f'exception point 1: {e}')
                if endCount == 1:
                    break

                if js['_next']:
                    cursor = js['_next']
                    print(f'{chat_df.iloc[-1, 6]}: {chat_df.iloc[-1, 4]}/{duration}')

                count = count + 1

            except Exception as e:
                print(f'exception point 2: {e}')
                break

    def run(self, vod, data_path):
        # 비디오 채팅 원본 받아서 저장
        chat_df = pd.DataFrame(
            columns=['chat_id', 'video_id', 'user_id', 'created_at', 'offset_sec', 'message_idx', 'message'])
        with open(f'{data_path}/chat.csv', mode='w', newline='', encoding='utf-8') as file:
            chat_df.to_csv(file,
                           header=['chat_id', 'video_id', 'user_id', 'created_at', 'offset_sec', 'message_idx', 'message'],
                           index_label=False,
                           index=False,
                           encoding='utf-8')
            self.get_video_comments(config('API_KEY'), vod, file)
