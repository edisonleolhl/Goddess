# -*- coding:utf-8 -*-
import scrapy
import re
import os
import urllib.request

class GoddessSpider(scrapy.Spider):
    name = "goddess"
    start_urls = ['https://www.nvshens.com/rank/sum/4.html']

    def parse(self, response):
        # follow links to goddess pages
        for href in response.css('div.rankli_imgdiv a::attr(href)'):
            yield response.follow(href, self.parse_goddess)

        # follow pagination links
        next_page = None
        L = len(response.css('div.pagesYY a::attr(href)'))
        for i in range(L):
            tmp_page = re.findall(r"[1-5].html", str(response.css('div.pagesYY a::attr(href)')[i]))
            print("tmp_page=", tmp_page)
            cur_page = re.findall(r"[1-5].html", str(response.css('div.pagesYY a.cur::attr(href)')))
            print("cur_page=", cur_page)
            if tmp_page == cur_page and cur_page != ['5.html']:
                next_page = response.css('div.pagesYY a::attr(href)')[i+1]
                print("next_page=", next_page)
                break
        if next_page is not None:
            print("--------------------------------------------------------------------")
            yield response.follow(next_page, self.parse)

    def parse_goddess(self, response):
        # get goddess info, like name, age, birthday ...
        def util(self, l):
            if l is not None and len(l) != 0:
                return l[0]
            else:
                return None
        dic = dict(zip(response.css('div.infodiv td::text').extract()[0::2], response.css('div.infodiv td::text').extract()[1::2]))
        dic['姓名'] = response.css('div.div_h1 h1::text').extract()[0]
        yield dic

        # get to the album page (before photo page) or photo page directly
        if response.css('span.archive_more a::attr(href)') is not None:
            for archive_more in response.css('span.archive_more a::attr(href)'):
                yield response.follow(archive_more, self.parse_goddess_album)
        else:
            for album_link in response.css('a.igalleryli_link::attr(href)'):
                yield response.follow(album_link, self.parse_goddess_photo)

    def parse_goddess_album(self, response):
        # traverse
        for album_link in response.css('a.igalleryli_link::attr(href)'):
            yield response.follow(album_link, self.parse_goddess_photo)

    def parse_goddess_photo(self, response):
        # NOW U ARE IN PHOTO PAGE!
        # download photo
        album_title = response.css('h1#htilte::text').extract_first()
        album_desc = response.css('div#ddesc::text').extract_first()
        album_info = response.css('div#dinfo span::text').extract_first() + response.css('div#dinfo::text').extract()[1]
        path = 'goddess_photo/' + album_title + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + 'album_info.txt', 'w+') as f:
            f.write(album_desc)
            f.write(album_info)
        for img_src in response.css('ul#hgallery img::attr(src)').extract():
            with open(path + "".join(re.findall(r"[0-9]{1,4}.jpg", img_src)), 'wb+') as f_img:
                f_img.write(urllib.request.urlopen(img_src).read())
                print("DOWALOADING img_src:" + img_src)

        # follow pagination links
        next_page = response.css('a.a1::attr(href)')[1]
        if next_page is not None:
            print("".join(re.findall(r"..html", str(next_page))) + '--> next_page:' + album_title)
            yield response.follow(next_page, self.parse_goddess_photo)