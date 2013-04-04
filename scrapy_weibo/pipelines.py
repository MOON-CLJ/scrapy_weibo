import simplejson as json

class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('items.jl', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(item.to_dict()) + "\n"
        self.file.write(line)
        return item
