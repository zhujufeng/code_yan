from DrissionPage import Chromium
import pandas as pd
import time
# --- 数据存储初始化 ---
# cars_list: 存储汽车基本信息的列表
cars_list = []
# comments_list: 存储评论文本信息的列表
comments_list = []

# 启动 Chromium 浏览器并获取最新标签页
tab = Chromium().latest_tab

# 打开销量页面 URL
url = 'https://www.dongchedi.com/auto/library/x-x-x-x-x-x-4-x-x-x-x'
tab.get(url)
# 等待页面开始加载，超时时间 3 秒
tab.wait.load_start(3)

# 获取页面上近三个月新能源汽车销量排行的所有车辆卡片元素
car_rank = tab.eles('xpath://div[@class="series-card_root__1ja7l car-list_card__1BJSa"]')
# 仅抓取排名第n到第m的车辆（可根据需求调整）
for car in car_rank[4:7]:
    # 点击卡片，进入车型详情页
    car.click()
    # 切换到新打开的标签页并等待加载
    new_tab = Chromium().latest_tab
    new_tab.wait.load_start(3)

    # 点击“口碑”选项卡，查看用户评论
    new_tab.eles('xpath://a[@class="top-anchor_anchor__2e6sy"]')[3].click()
    new_tab = Chromium().latest_tab
    new_tab.wait.load_start(3)

    # ------- 爬取车型基本信息 -------
    # 获取车型名称
    car_name = new_tab.ele('xpath://h1[@class="tw-flex tw-items-center tw-my-6 md:tw-my-8 lg:tw-my-10 xl:tw-my-12"]/span/span[2]').text
    print(f'正在爬取{car_name}的详细信息')
    # 获取官方指导价
    car_price = new_tab.ele('xpath://span[@class="jsx-2173306956 style_priceLeftText__JPECu tw-w-112"]').text

    # 获取各维度口碑评分：外观、内饰、配置、空间、舒适性、操控、动力
    vehicle_appearance = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[0].text
    vehicle_interior = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[1].text
    vehicle_configuration = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[2].text
    vehicle_space = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[3].text
    vehicle_comfort = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[4].text
    vehicle_control = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[5].text
    vehicle_power = new_tab.eles('xpath://ul[@class="jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null"]/li[2]')[6].text

    # 将本次抓取到的基本信息存入列表
    cars_list.append({
        'car_name': car_name,
        'car_price': car_price,
        'vehicle_appearance': vehicle_appearance,
        'vehicle_interior': vehicle_interior,
        'vehicle_configuration': vehicle_configuration,
        'vehicle_space': vehicle_space,
        'vehicle_comfort': vehicle_comfort,
        'vehicle_control': vehicle_control,
        'vehicle_power': vehicle_power
    })

    # 每抓取一个车型信息后暂停 3 秒，避免过于频繁
    time.sleep(3)

    # ------- 翻页爬取评论内容 -------
    # 仅抓取前 5 页评论
    for i in range(5):
        new_tab = Chromium().latest_tab
        # 滚动到底部，加载更多评论
        new_tab.scroll.to_bottom()
        time.sleep(5)
        # 遍历当前页的所有评论入口元素
        for k, j in enumerate(new_tab.eles('xpath://p[@class="line-4 tw-text-16 tw-leading-26 tw-cursor-pointer"]')):
            print(f'正在爬取{car_name}的第{i+1}页的第{k+1}条评论')
            # 获取评论对应的车型配置或版本信息
            car_detail = new_tab.eles('xpath://span[@class="tw-ml-4 tw-font-bold tw-text-16"]')[k].text
            # 确保该评论在可见区域
            new_tab.eles('xpath://span[@class="tw-ml-4 tw-font-bold tw-text-16"]')[k].scroll.to_see()
            new_tab.eles('xpath://span[@class="tw-ml-4 tw-font-bold tw-text-16"]')[k].wait.displayed()
            # 点击查看完整评论
            j.click()
            new_tab1 = Chromium().latest_tab
            new_tab1.wait.load_start(3)
            # 获取评论文字内容
            content = new_tab1.ele('xpath://span[@class="jsx-2380637827"]').text

            # 将评论信息存入列表
            comments_list.append({
                'car_detail': car_detail,
                'content': content
            })
            # 关闭当前评论详情页，返回主标签页
            new_tab1.close()
            time.sleep(3)
        # 点击下一页按钮继续抓取
        new_tab.ele('xpath://i[@class="jsx-1325911405 DCD_Icon icon_into_12 tw-text-14"]').click()

    # 关闭车型详情页，继续下一个车型的抓取
    new_tab.close()

# 全部抓取完成后打印结束提示
print('爬取结束。')

# --- 创建并展示 DataFrame ---
print("\n--- 正在创建 DataFrame ---")
# 将列表转换为 pandas DataFrame
df_cars = pd.DataFrame(cars_list)
df_comments = pd.DataFrame(comments_list)

print("\n--- DataFrame: 汽车 (Cars) ---")
print(df_cars.head(), f"形状: {df_cars.shape}")

print("\n--- DataFrame: 评论 (Comments) ---")
print(df_comments.head(), f"形状: {df_comments.shape}")

# 将数据保存到本地 Excel 文件（请确认路径存在）
output_path_cars = "E:\\paper\\cars3.xlsx"
output_path_comments = "E:\\paper\\comments3.xlsx"
df_cars.to_excel(output_path_cars, index=False, engine='openpyxl')
df_comments.to_excel(output_path_comments, index=False, engine='openpyxl')
print(f"数据已保存到 {output_path_cars} 和 {output_path_comments}")
