# FanFouSpider
饭否爬虫, 根据用户ID搜集.支持词云展示，发贴时间统计，关键词搜索，数据库更新等功能。
## Requirement
- python3.6
- mysql5.7
- PyMySQL
- fire
## How to collect information 
1. Create database "spider"

2. Config headers
  - Sign in Fanfou
  - Open chrome F12, input URL: https://fanfou.com/[UserID]
  - Click Network(top side)->fanfou.com(left side)->Request Headers
  - Copy the corresponding parameters to **self.headers**
  
3. Configure self.table_name used to store the data 

4. User ID can be found in the URL of the profile page
   ```
    python FanFouSpider.py start [UserID] --table=[TableName]
   ```
  
## How to collect information based on keywords
```bash
python FanFouSpider.py key_word [TableName] [KeyWord]
```
## How to draw some analysis charts

```bash
# dump to csv
python FanFouSpider.py dump [TableName]
# draw charts, find them in ./output/
python analytics.py draw [TableName]
```
## Examples
![WordCloud](https://github.com/asdf0982/FanFouSpider/raw/master/output/test_wordcloud.png)
![DaylyChart](https://github.com/asdf0982/FanFouSpider/raw/master/output/test_day_chart.png)
![MonthlyChart](https://github.com/asdf0982/FanFouSpider/raw/master/output/test_month_chart.png)