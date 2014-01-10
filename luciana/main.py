import cgi
import urllib

import webapp2

from google.appengine.ext import ndb


class Mention(ndb.Model):
    """Models a mention of a word in a line of a Shakespear's work."""
    line = ndb.StringProperty()
    work = ndb.StringProperty()


class Word(ndb.Model):
  """Models a word containing its name and a list of works and lines in which occurs."""
  name = ndb.StringProperty()
  mentions = ndb.StructuredProperty(Mention, repeated=True)

  @classmethod
  def query_repo(cls, ancestor_key):
    return cls.query(ancestor=ancestor_key)


class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')
    
    self.response.out.write("""
          <form action="/find" method="post">
            <h3>Find word</h3>
            <div><input name="word_search"/></div>
          </form>
          <form action="/insert" method="post">
            <h3>Insert a new occurence</h3>            
            <div>Word</div>
            <div><input name="word"/></div>
            <div>Work</div>
            <div><input name="work"/></div>
            <div>Line</div>
            <div><input name="line"/></div>
            <div><input type="submit" value="Insert"></div>
          </form>
          <hr>
        </body>
      </html>""")

    ancestor_key = ndb.Key('Index', 'Shakespeare')
    repo = Word.query_repo(ancestor_key).fetch(20)

    for word in repo:
        self.response.out.write('<div><b>%s</b></div><div><ul>' % cgi.escape(word.name))
        for mention in word.mentions:
            self.response.out.write("""
                <li>
                    <div>Work: %s</div>
                    <div>Line: <i>%s</i></div>
                </li>""" % (cgi.escape(mention.work),
                            cgi.escape(mention.line)))
        self.response.out.write('</ul>')


class SubmitForm(webapp2.RequestHandler):
  def post(self):
    word = Word.get_by_id(cgi.escape(self.request.get('word')), parent=ndb.Key('Index', 'Shakespeare'))
    print "-----------------------" + str(word)
    print "-----------------------" + cgi.escape(self.request.get('word'))
    if not word:
        word = Word(parent=ndb.Key('Index', 'Shakespeare'), 
                id=cgi.escape(self.request.get('word')),
                name=cgi.escape(self.request.get('word')))
    print "-----------------------" + str(word)
    new_mention = Mention(line=self.request.get('line'), 
                          work=self.request.get('work'))
    # print "-----------------------" + str(new_mention)
    if word.mentions:
        word.mentions.append(new_mention)
    else:
        word.mentions = [new_mention]
    print "-----------------------" + str(word.mentions)
        
    word.put()
    self.redirect('/')


app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/insert', SubmitForm)
])
