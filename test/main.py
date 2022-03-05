import pymongo as pymongo
# python3 -m pip install pymongo[srv]
import requests

from urllib import parse
from enum import Enum
from pymongo.server_api import ServerApi
from requests import Response


def mongodbConnection():
    client = pymongo.MongoClient(
        "mongodb+srv://cederjtcc:" + parse.quote("4uAvN@AqBnwAS7W") + "@cluster0.kdtav.mongodb.net/test?retryWrites=true&w=majority",
        server_api=ServerApi('1'))
    return client.test


def buildUrl(options: list):
    url = '/'.join(options)
    return url


class TypeResponse(Enum):
    json = 'json'
    text = 'text'
    none = None


def getInfoFromItems(content: dict, info):
    items: list = content['items']
    return [i[info] for i in items]


class BloggerScrapper:
    def __init__(self):
        self.apiKey = 'AIzaSyCGj3uCrU2wD06QuplLnzDM9dVWJR6tDRU'
        self.baseUrl = 'https://www.googleapis.com/blogger/v3/blogs'
        self.requestMethods = {'get': 'GET', 'post': 'POST'}

    def request(self, method: str, url: str, typeResponse: TypeResponse, query=None) -> Response or str or dict:
        if query is None:
            query = {}

        url = url + '?key=' + self.apiKey

        if 'url' in query:
            url += '&url=' + query['url']
        if 'maxResults' in query:
            url += '&maxResults=' + query['maxResults']

        response: Response = requests.request(method, url)

        if typeResponse == TypeResponse.json:
            return response.json()
        if typeResponse == TypeResponse.text:
            return response.text
        return response

    def requestBlogIdByUrl(self, blogUrl):
        method = self.requestMethods.get('get')
        url = buildUrl([self.baseUrl, 'byurl'])
        response: dict = self.request(method, url, TypeResponse.json, {'url': blogUrl})
        if 'id' not in response:
            return None
        return response['id']

    def getBlogById(self, blogId: str):
        method = self.requestMethods.get('get')
        url = buildUrl([self.baseUrl, blogId])
        return self.request(method, url, TypeResponse.json)

    def getPostById(self, blogId: str, postId: str):
        method = self.requestMethods.get('get')
        url = buildUrl([self.baseUrl, blogId, 'posts', postId])
        return self.request(method, url, TypeResponse.json)

    def getCommentById(self, blogId: str, postId: str, commentId: str):
        method = self.requestMethods.get('get')
        url = buildUrl([self.baseUrl, blogId, 'posts', postId, 'comments', commentId])
        return self.request(method, url, TypeResponse.json)

    def getPostsFromBlog(self, blogId: str) -> dict:
        method = self.requestMethods.get('get')
        url = buildUrl([self.baseUrl, blogId, 'posts'])
        blog: dict = self.request(method, url, TypeResponse.json, {'maxResults': '10'})
        if 'items' not in blog:
            return {}

        response: dict = {'postsIds': getInfoFromItems(blog, 'id'), 'titles': getInfoFromItems(blog, 'title'),
                          'contents': getInfoFromItems(blog, 'content')}
        return response

    def getCommentsFromPost(self, blogId: str, postId: str) -> list:
        method = self.requestMethods.get('get')
        url = buildUrl([self.baseUrl, blogId, 'posts', postId, 'comments'])
        comments: dict = self.request(method, url, TypeResponse.json)
        if 'items' not in comments:
            return []
        return getInfoFromItems(comments, 'content')

    def getAllCommentsFromPosts(self, blogId: str, content: list):
        return [self.getCommentsFromPost(blogId, i) for i in content]


if __name__ == '__main__':
    # connection = mongodbConnection()
    blogger = BloggerScrapper()
    blogId = blogger.requestBlogIdByUrl('https://gallagherlawlibrary.blogspot.com/')
    blogAllPosts = blogger.getPostsFromBlog(blogId)
    blogAllPosts['comments'] = blogger.getAllCommentsFromPosts(blogId, blogAllPosts['postsIds'])
    # print(blogAllPosts)
    for i in range(len(blogAllPosts['postsIds'])):
        print('id ', blogAllPosts['postsIds'][i])
        print('title ', blogAllPosts['titles'][i])
        # print('content ', blogAllPosts['contents'][i][::4] + '...')
        print('comments ', blogAllPosts['comments'][i])
        print('\n')
