import os
import re
import pandas as pd
import jieba
from collections import Counter
from snownlp import SnowNLP
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import math

plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体

# 加载数据
df = pd.read_excel(r"E:\paper\comments.xlsx")


# 情感分析函数
def get_sentiment(text):
    s = SnowNLP(text)
    return s.sentiments


def classify_sentiment(score):
    if score >= 0.6:
        return 'positive'
    elif score <= 0.4:
        return 'negative'
    else:
        return 'neutral'


# 计算情感分数与分类
df['sentiment'] = df['content'].apply(get_sentiment)
df['sentiment_class'] = df['sentiment'].apply(classify_sentiment)

# 统计各品牌情感
average_sentiment = df.groupby('brand')['sentiment'].mean()
num_reviews = df.groupby('brand').size()
sentiment_dist = df.groupby('brand')['sentiment_class'].value_counts(normalize=True).unstack(fill_value=0)

# 停用词列表
stop_words = {
    "的", "了", "和", "是", "我", "也", "就", "都", "很", "还", "在", "有", "不", "吧", "还是", "没有",
    "可以", "就是", "感觉", "但是", "非常", "特别", "那么", "因为", "自己", "不是", "不过", "太低", "很多",
    "一个", "时候", "左右", "一点", "所以", "真的", "这个", "比较", "选择", "感受", "一下", "确实",
    "还有", "问题", "方面", "如果", "目前", "之前", "一些", "时间", "可能", "需要", "的话", "觉得",
    "有点", "来说", "而且", "什么", "已经", "起来", "开始", "使用", "直接", "完全", "其他", "个人",
    "对于", "虽然", "不会", "基本", "现在", "表现", "知道", "考虑", "情况", "地方", "一般", "一直",
    "毕竟", "然后", "最后", "最不满意", "提车", "购车经历"
}


# 关键词提取函数
def extract_keywords(text, top_n=10):
    text = re.sub(r'[^\w\s]', '', text)
    words = jieba.cut(text, cut_all=False)
    words = [w for w in words if w not in stop_words and len(w) > 1]
    counter = Counter(words)
    return counter.most_common(top_n)


# 每品牌关键词
content_per_car = df.groupby('brand')['content'].apply(lambda x: ' '.join(x))
keywords_per_car = content_per_car.apply(lambda x: extract_keywords(x))

# 全量词频（Top 50）
all_content = ' '.join(df['content'])
words = jieba.cut(all_content, cut_all=False)
word_list = [w for w in words if w not in stop_words and len(w) > 1]
word_freq = Counter(word_list).most_common(50)

# 生成整体词云并保存
os.makedirs('plots', exist_ok=True)
wc_all = WordCloud(
    width=800, height=400,
    background_color='white',
    font_path='simhei.ttf'
).generate_from_frequencies(dict(word_freq))
plt.figure(figsize=(10, 5))
plt.imshow(wc_all, interpolation='bilinear')
plt.axis('off')
plt.title('所有品牌评论整体词云')
plt.tight_layout()
plt.savefig('plots/wordcloud_all_brands.png', dpi=300)
plt.show()

# 打印统计结果
print("平均情感得分：\n", average_sentiment)
print("\n评论数量：\n", num_reviews)
print("\n情感分布：\n", sentiment_dist)
print("\n关键词（每品牌Top 10）：\n", keywords_per_car)
print("\n整体词云词频（Top 50）：\n", word_freq)

# —— 1. 各品牌平均情感得分柱状图 —— #
plt.figure(figsize=(12, 6))
average_sentiment.sort_values().plot(kind='bar')
plt.title('各品牌平均情感得分', fontsize=16)
plt.ylabel('平均情感得分')
plt.xlabel('品牌')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('plots/average_sentiment_by_brand.png', dpi=300)
plt.show()

# —— 2. 每个品牌单独生成词云图 —— #
os.makedirs('wordclouds', exist_ok=True)

brands = df['brand'].unique()
n = len(brands)
cols = 3  # 每行放 3 张子图，你也可以改成 2 或 4
rows = math.ceil(n / cols)

fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
axes = axes.flatten()

for idx, brand in enumerate(brands):
    text = ' '.join(df[df['brand'] == brand]['content'].astype(str))
    wc = WordCloud(
        width=800, height=400,
        background_color='white',
        font_path='simhei.ttf',
        stopwords=stop_words
    ).generate(text)

    ax = axes[idx]
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'{brand} 评论词云', fontsize=14)

# 隐藏多余的子图
for ax in axes[n:]:
    ax.axis('off')

plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/wordclouds_all_brands.png', dpi=300)
plt.show()
