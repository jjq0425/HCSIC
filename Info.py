'''
This section defines the code for Info class
'''

import struct


class Info:
    def __init__(self,  content, type, infoStruct_Type=0):
        self.content = content
        self.type = type

        '''
        For the sake of simplicity during queries, it is set to string format and infoStructureType is set to 1
        '''
        if infoStruct_Type == 1:
            self.Info_struct = struct.Struct('8sI')
        else:
            self.Info_struct = struct.Struct('40sI')

    def getInfo_Struct(self):
        return self.Info_struct

    def serialize(self):
        # Serialize each IOT information
        return self.Info_struct.pack(self.content.encode('utf-8'), self.type)


@staticmethod
def deserialize(data, infoStruct_Type=0):
    if infoStruct_Type == 1:
        Info_struct = struct.Struct('8sI')
    else:
        Info_struct = struct.Struct('40sI')
    # Deserialize each information
    content, type = Info_struct.unpack(data)
    # print(">> Encode Message:", content.decode('utf-8'))
    return Info(content.decode('utf-8'), type)
