from django.shortcuts import render
from django.views.decorators.http import require_GET
from .models import Streamer, Video, Data
from .mkclip.twighlight.chat import Collector
from .mkclip.twighlight.preprocess import Preprocessor
from .mkclip.twighlight.model import Analyser, ClipMaker
import numpy as np
import pandas as pd

@require_GET
def index(request):
    context = {
        'latest_question_list': "test",
    }
    return render(request, 'home.html', context)

@require_GET
def streamer(request):
    streamers = Streamer.objects.all()
    context = {'streamers': streamers}
    return render(request, 'streamer.html', context)


# video 의 리스트
@require_GET
def video(request, streamer_sid):
    streamer_instance = Streamer.objects.get(sid=streamer_sid)
    videos = Video.objects.filter(streamer_id=streamer_instance.id)
    context = {'videos': videos, 'streamer': streamer_instance}
    return render(request, 'video_list.html', context)


@require_GET
def chat(request, streamer_sid, video_vid):
    video = Video.objects.get(vid=video_vid)
    datas = Data.objects.filter(video_id=video.id)
    if len(datas) == 0:
        # date time을 chat으로부터 가지고 와야함.
        collector = Collector()
        preprocessor = Preprocessor()
        analyser = Analyser()
        clip_maker = ClipMaker()
        collector.run(vod=video_vid, data_path='./boards/mkclip/data/')
        preprocessor.run(data_path='./boards/mkclip/data/', data_name='chat.csv', d2v_file='./boards/mkclip/model/d2v_model')
        clips = clip_maker.run(result=analyser.run(data_file='./boards/mkclip/data/ppd.npy',
                                                   model_file='./boards/mkclip/model/rnn_model.h5'),
                              chat_file='./boards/mkclip/data/chat.csv')

        # for 문을 돌려서 입력한 시간의 갯수만큼 버튼을 만들건데, for문을 def Data Table을 통해 돌릴 것이기 때문.
        for clip in clips:
            data = Data(data_time=int(clip), video_id_id=video.id, streamer_id_id=video.streamer_id.id)
            data.save()

    # video로 돌릴경우 시간 값을 뽑을 수가없다. for문을 돌려서 걸리는 시간값만큼 button 생성.
    data_instance = Data.objects.filter(video_id_id=video.id)
    streamer_instance = Streamer.objects.get(sid=streamer_sid)
    video = Video.objects.get(vid=video_vid)
    context = {'video': video, 'streamer': streamer_instance, 'datas': data_instance}
    return render(request, 'chat.html', context)
