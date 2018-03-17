#!/usr/bin/env python
#coding:utf-8
#Created by Andy @ 2018/3/15




class Pagination(object):

    def __init__(self, current_page, total_pages, base_url, params, items_per_page=10, max_pages_count=11):
        """

        :param current_page: current page num
        :param total_pages: total pages
        :param base_url:
        :param params: the request.GET
        :param items_per_page:
        :param max_pages_count:
        """
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1

        if current_page <= 0:
            current_page = 1
        self.current_page = current_page
        self.total_pages = total_pages
        self.items_per_page = items_per_page

        # 页面上应该显示的最大页码
        max_page_num, div = divmod(total_pages, items_per_page)
        if div:
            max_page_num += 1
        self.max_page_num = max_page_num

        # 页面上默认显示11个页面（当前页在中间）
        self.max_pages_count = max_pages_count
        self.half_max_pages_count = int((max_pages_count - 1) / 2)

        # URL前缀
        self.base_url = base_url

        # request.GET
        # the params is set to unmutable, you need to change it
        import copy
        params = copy.deepcopy(params)
        params._mutable = True
        self.params = params

    @property
    def start(self):
        """
        The start page num
        :return:
        """
        return (self.current_page - 1) * self.items_per_page

    @property
    def end(self):
        """
        The end of page num in every page
        :return:
        """
        return self.current_page * self.items_per_page

    def page_html(self):
        """
        render page in html
        :return:page_html
        """
        if self.max_page_num <= self.max_pages_count:
            pager_start = 1
            pager_end = self.max_page_num
        # 如果总页数 > 11
        else:
            # 如果当前页 <= 5
            if self.current_page <= self.half_max_pages_count:
                pager_start = 1
                pager_end = self.max_pages_count
            else:
                # 当前页 + 5 > 总页码
                if (self.current_page + self.half_max_pages_count) > self.max_page_num:
                    pager_end = self.max_page_num
                    pager_start = self.max_page_num - self.max_pages_count + 1
                else:
                    pager_start = self.current_page - self.half_max_pages_count
                    pager_end = self.current_page + self.half_max_pages_count

        page_html_list = []

        # set the first page
        if self.current_page > self.max_pages_count:
            self.params['page'] = 1
            first_page = '<li><a href="%s?%s">First</a></li>' % (self.base_url, self.params.urlencode(),)
            page_html_list.append(first_page)

        # if has previous page set previous or disabled the button
        if self.current_page <= 1:
            pre_page = "<li class='disabled'><a href='#'>Previous</a></li>"
        else:
            self.params["page"] = self.current_page - 1
            pre_page = "<li><a href='%s?%s'>previous</a></li>" %(self.base_url, self.params.urlencode(),)
        page_html_list.append(pre_page)


        for i in range(pager_start, pager_end + 1):
            self.params['page'] = i
            if i == self.current_page:
                temp = '<li class="active"><a  href="%s?%s">%s</a></li>' % (self.base_url, self.params.urlencode(), i,)
            else:
                temp = '<li><a href="%s?%s">%s</a></li>' % (self.base_url, self.params.urlencode(), i,)
            page_html_list.append(temp)

        # if has next page set next or disabled it
        if self.current_page >= self.max_page_num:
            next_page = '<li class="disabled"><a href="#">Next</a></li>'
        else:
            self.params["page"] = self.current_page + 1
            next_page = '<li><a href="%s?%s">Next</a></li>' % (self.base_url, self.params.urlencode(),)
        page_html_list.append(next_page)

         # set the last page
        if self.current_page + self.max_pages_count < self. total_pages:
            self.params['page'] = self.max_page_num
            last_page = '<li><a href="%s?%s">End</a></li>' % (self.base_url, self.params.urlencode(),)
            page_html_list.append(last_page)

        return ''.join(page_html_list)