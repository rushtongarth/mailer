import torchtext

# inspired by:
## https://github.com/pytorch/text/issues/488

class DataFrameDataset(torchtext.data.Dataset):
  """Class for using pandas DataFrames as a datasource"""
  def __init__(self, examples, fields, filter_pred=None):
    """
    Create a dataset from a pandas dataframe of examples and Fields
    Arguments:
    
    :param examples: DataFrame of examples
    :type examples: :class:`pandas.DataFrame`
    :param fields: Fields to use, where keys are field names, and values are the associated fields.
    :type fields: dict
    :param filter_pred: use only exanples for which filter_pred(example) is true, or use all examples if None.
    :type filter_pred: (callable or None)
    """
    self.examples = examples.apply(SeriesExample.fromSeries, args=(fields,), axis=1).tolist()
    if filter_pred is not None:
      self.examples = list(filter(filter_pred, self.examples))
    self.fields = dict(fields)
    # Unpack field tuples
    for n, f in self.fields.items():
      if isinstance(n, tuple):
        self.fields.update(zip(n, f))
        del self.fields[n]

class SeriesExample(torchtext.data.Example):
  """Class to convert a pandas Series to an Example"""
  @classmethod
  def fromSeries(cls, data, fields):
    return cls.fromdict(data.to_dict(), fields)

  @classmethod
  def fromdict(cls, data, fields):
    ex = cls()

    for key, field in fields.items():
      if key not in data:
        ostr = "Key '{}' was not found in input data"
        raise ValueError(ostr.format(key))
      if field is not None:
        setattr(ex, key, field.preprocess(data[key]))
      else:
        setattr(ex, key, data[key])
    return ex
