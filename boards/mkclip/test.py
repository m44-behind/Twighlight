from .twighlight.chat import Collector
from .twighlight.preprocess import Preprocessor
from .twighlight.model import Analyser, ClipMaker

if __name__ == '__main__':
    collector = Collector()
    collector.run(427407092, './data')
    preprocessor = Preprocessor()
    preprocessor.run('./data/', 'chat.csv', './model/d2v_model')
    model = Analyser()
    cm = ClipMaker()
    result = cm.run(model.run('./data/ppd.npy', './model/rnn_model.h5'), './data/chat.csv')
    print(result)
