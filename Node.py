

'''
Description: This section defines the code for node class
'''


class Node:
    def __init__(self, node_id, is_byzantine):
        self.node_id = node_id
        # Node ID
        self.is_byzantine = is_byzantine
        # Is the node a malicious node (Byzantine node)
        # self.OriginalData = []
        self.storageOriginal = bytearray(b'')
        # The encoded original message stored by the node
        self.storageRedundant = bytearray(b'')
        # Redundant value sharded data stored after encoding
        self.RedundantIndex = -1
        # Redundant sharding index

    '''
    Add storage information
    '''

    def ADDstorage(self, content, redundant, index, Datalen):

        self.storageOriginal = content
        self.storageRedundant = redundant  # Redundant sharding
        self.RedundantIndex = index  # Redundant sharding index
        # for i in range(len(content)//Datalen):
        #     self.OriginalData.append(deserialize
        #                              (content[i*Datalen:(i+1)*Datalen]))

    def get_storage_size(self):
        """
        Obtain occupied storage space
        """
        return len(self.storageOriginal)+len(self.storageRedundant)

    def getStorageOriginal(self):
        """
        Obtain stored raw data

        :return: Bytestring of raw data
        :descrption: If it is a Byzantine node, return an meaningless byte string
        """
        if self.is_byzantine:
            return bytearray(len(self.storageOriginal))
        else:
            return self.storageOriginal

    def getStorageRedundant(self):
        """
        Obtain storage redundancy value

        Returns:A byte array for storing redundant values
        :descrption: If it is a Byzantine node, return an meaningless byte string
        """
        if self.is_byzantine:
            return bytearray(len(self.storageRedundant))
        else:
            return self.storageRedundant

# Count the number of Byzantine nodes


def sumOfbyzantine(nodes):
    sum = 0
    for node_ in nodes:
        if node_.is_byzantine:
            sum += 1
    return sum
