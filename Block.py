'''
This section defines the code for Block class
'''

import reedsolo


class Block:
    def __init__(self, OriginalContent):
        self.OriginalContent = OriginalContent
        # Original data information (in array form, with IoTInfo objects as elements)
        self.DataNum = len(OriginalContent)
        self.Datalen = 0

        self.EcondedContent = bytearray(b'')
        self.RedundantContent = bytearray(b'')

        self.EcondedContentSUM = bytearray(b'')
        # Encoding+redundant data: This data is only temporarily stored as an intermediate variable

    def getBlockSize(self):
        # Obtain the size of unshipped block information (used to query the storage cost of the full storage strategy)
        return len(self.EcondedContent)

    def GenrSerialData(self):
        # Serialize OriginalContent for subsequent encoding
        for i in range(len(self.OriginalContent)):
            self.EcondedContent += self.OriginalContent[i].serialize()

        self.Datalen = len(self.OriginalContent[0].serialize())

    '''
    RS encoding function & generating redundant values
    '''

    def EncodeMY(self, ByzantineNodesNum, InfoNumNodesGet):
        '''
           Create a reedsolo object, passing in parameters of at most how many byte errors can be corrected
        '''
        rs = reedsolo.RSCodec(
            int(self.Datalen*ByzantineNodesNum*InfoNumNodesGet))

        # 对其进行编码
        self.EcondedContentSUM = rs.encode(self.EcondedContent)

        # The last part of the encoding is redundant data, and the first part is the same as before the encoding  (detailed in Article 3.3)
        self.RedundantContent = self.EcondedContentSUM[(
            self.Datalen*self.DataNum):]

    '''
    Decoding function
    '''

    def Decode(self, data, ByzantineNodesNum, InfoNumNodesGet, erase_pos=[]):
        # 构建reedsolo对象
        # print("debug:", erase_pos)
        rs = reedsolo.RSCodec(
            int(self.Datalen*ByzantineNodesNum*InfoNumNodesGet))

        return rs.decode(data, erase_pos=erase_pos)[0]
