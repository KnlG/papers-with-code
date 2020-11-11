# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field

class SotaSpider(scrapy.Spider):
	name = 'sota'
	# allowed_domains = ['www.paperswithcode.com/sota']
	start_urls = ['http://paperswithcode.com/sota/']

	# class TreeNode():
	# 	def __init__(self, name, children=None):
	# 		self.name = name
	# 		self.children = list(children) if children is not None else []

	# 	def add_child(child):
	# 		self.children.append(child)

	def parse(self, response):
		fields = response.css("h4 a::text").getall()
		yield dict(zip(range(len(fields)), fields))
		next_pages = response.css("div.sota-all-tasks a::attr(href)").getall()
		for page in next_pages:
			next_page = response.urljoin(page)
			yield scrapy.Request(next_page, callback=self.parse_subfields)

	def parse_subfields(self, response):
		field = response.css("h1::text").get()
		subfields = response.css("h4::text").getall()
		# map(str.strip, subfields)
		for i in range(len(subfields)):
			subfields[i]= str(subfields[i]).strip()
		task_pages = response.css("div.sota-all-tasks a::attr(href)").getall()
		# mydict = { i : "" for i in subfields }
		c = 0
		for page in task_pages:
			next_page = response.urljoin(page)
			request = scrapy.Request(next_page, callback=self.parse_tasks, meta = {"subfield": subfields[c]})
			yield request
			# mydict[subfields[c]]= {i : papers for i in tasks}
			c+=1
		yield {"field" : field, "subfields" : dict(zip(range(len(subfields)), subfields))}
		# yield {field : subfields}

	def parse_tasks(self, response):
		subfield = response.meta["subfield"]
		tasks = response.css("h1.card-title::text").getall()
		subtask_pages = response.css("div.card a::attr(href)").getall()
		c = 0
		for page in subtask_pages:
			next_page = response.urljoin(page)
			yield scrapy.Request(next_page, callback=self.parse_subtasks, meta = {"task": tasks[c]})
			c+=1
		yield {"subfield" : subfield, "tasks" : dict(zip(range(len(tasks)), tasks))}

	def parse_subtasks(self, response):
		task = response.meta["task"]
		subtasks = response.css("div:not(.text-center).paper a::text").getall()
		paper_pages = response.css("div.text-center.paper a::attr(href)").getall()
		c = 0
		for page in paper_pages:
			next_page = response.urljoin(page)
			yield scrapy.Request(next_page, callback=self.parse_abstracts, meta={"paper":subtasks[c]})
			c+=1
		yield {"task" : task, "papers" : dict(zip(range(len(subtasks)), subtasks))}

	def parse_abstracts(self, response):
		paper = response.meta["paper"]
		a1 = str(response.css("div.paper-abstract p::text").get()).strip()
		a2 = str(response.css("div.paper-abstract p span+span::text").get()).strip()
		abstract = a1+a2
		return {"paper" : paper, "abstract" : abstract}