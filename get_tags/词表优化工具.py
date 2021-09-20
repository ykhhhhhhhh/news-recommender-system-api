import pandas as pd

# 删掉点烂词
words_lists = pd.read_csv(r'D:\Projects\新闻推荐\新闻推荐接口\get_tags\word_lists_72_20210404.csv')

tt = '混合，相关研究，使用寿命，俄罗斯，新技术，技术研究，化学物'
bad_words = tt.split('，')
for word in bad_words:
    words_lists.replace(word, '', inplace=True)
words_lists.to_csv('D:\Projects\新闻推荐\新闻推荐接口\get_tags\word_lists_72_20210918.csv', index=False, encoding='utf-8')
