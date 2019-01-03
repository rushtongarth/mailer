import abc
 

class AbstractArticle(abc.ABC):
  @abc.abstractmethod
  def __init__(self,date,title,link):
    pass
  @abc.abstractmethod
  def __repr__(self):
    pass
  @abc.abstractmethod
  def format_for_db(self):
    pass

