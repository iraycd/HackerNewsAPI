#!/usr/bin/env python
"""
Unofficial Python API for Hacker News.
Currently supports reading HN homepage and newest stories
page only.

@author: Karan Goel <karan@goel.im>
"""
import re
from urllib2 import urlopen

from bs4 import BeautifulSoup


BASE_URL = 'http://news.ycombinator.com'


class HN():
    """The class that parses the HN page, and builds up all Story objects"""
    
    
    def get_zipped_rows(self, soup):
        """Returns all 'tr' tag rows as a list of tuples. Each tuple is for
        a single story."""
        table = soup.findChildren('table')[2] # the table with all submissions
        rows = table.findChildren(['tr'])[:-2] # get all rows but last 2
        # remove the spacing rows
        spacing = xrange(2, len(rows), 3) # indices of spacing tr's
        rows = [row for (i, row) in enumerate(rows) if (i not in spacing)]
        # rank, title, domain
        info = [row for (i, row) in enumerate(rows) if (i % 2 == 0)]
        # points, submitter, comments
        detail = [row for (i, row) in enumerate(rows) if (i % 2 != 0)]

        return zip(info, detail) # build a list of tuple for all post
    
    
    def build_story(self, all_rows):
        """Builds and returns a complete Story object from
        the passed source."""
        all_stories = [] # list to hold all stories
        
        for (info, detail) in all_rows:
            #-- Get the into about a story --#
            info_cells = info.findAll('td') # split in 3 cells
            
            rank = int(info_cells[0].string[:-1])
            title = info_cells[2].find('a').string
            link = info_cells[2].find('a').get('href')
            try:
                domain = info_cells[2].find('span').string[2:-2] # slice " (abc.com) "
            except AttributeError:
                # this is a self post
                domain = ''
            #-- Get the into about a story --#
            
            #-- Get the detail about a story --#
            detail_cell = detail.findAll('td')[1] # split in 2 cells, we need only second
            detail_concern = detail_cell.contents # list of details we need, 5 count
            
            points = int(re.match(r'^(\d+)\spoint.*', detail_concern[0].string).groups()[0])
            submitter = detail_concern[2].string
            comment_tag = detail_concern[4]
            story_id = int(re.match(r'.*=(\d+)', comment_tag.get('href')).groups()[0])
            comments_link = '%s/item?id=%d' % (BASE_URL, story_id)
            comment_count = re.match(r'(\d+)\s.*', comment_tag.string)
            try:
                # regex matched, cast to int
                num_comments = int(comment_count.groups()[0])
            except AttributeError:
                # did not match, assign 0
                num_comments = 0
            #-- Get the detail about a story --#
            
            story = Story(rank, story_id, title, link, domain, points, submitter, 
                 num_comments, comments_link)
            
            all_stories.append(story)
        return all_stories
    
    
    def get_top_stories(self):
        """Returns a list of Story objects from the homepage
        of HN"""
        content = urlopen(BASE_URL).read()
        soup = BeautifulSoup(content)
        all_rows = self.get_zipped_rows(soup)
        return self.build_story(all_rows)
        
        
    def get_newest_stories(self):
        """Returns a list of Story objects from the newest page
        of HN"""
        content = urlopen('%s/newest' % BASE_URL).read()
        soup = BeautifulSoup(content)
        all_rows = self.get_zipped_rows(soup)
        return self.build_story(all_rows)
    


class Story():
    """Story class represents one single story on HN"""
    
    
    def __init__(self, rank, story_id, title, link, domain, points, submitter, 
                 num_comments, comments_link):
        self.rank = rank # the rank of story on the page
        self.story_id = story_id # the story's id
        self.title = title # the title of the story
        self.link = link # the url it points to (None for self posts)
        self.domain = domain # the domain of the link (None for self posts)
        self.points = points # the points/karma on the story
        self.submitter = submitter # the user who submitted the story
        self.num_comments = num_comments # the number of comments it has
        self.comments_link = comments_link # the link to the comments page


    def print_story(self):
        """Print the details of a story"""
        print 'Rank: %d' % self.rank
        print 'Story ID: %d' % self.story_id
        print 'Title: %s' % self.title.encode('cp850', errors='replace')
        print 'Link: %s' % self.link
        print 'Domain: %s' % self.domain
        print 'Points: %d' % self.points
        print 'Submitted by: %s' % self.submitter
        print 'Number of comments: %d' % self.num_comments
        print 'Link to comments: %s' % self.comments_link
        
    
    def __repr__(self):
        """A string representation of the class object"""
        return '{0} by {1}'.format(self.title, self.submitter)