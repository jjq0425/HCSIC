'''
Description: This code is an analysis of the storage cost of the system. We simulated the storage cost of each node from 3 to 18 nodes
'''

# import the nessessary libraries
from queue import Empty
import sys
import reedsolo
import math
import array
import struct
import time
import json
import matplotlib.pyplot as plt

# import the nessessary classes/functions/const Nums
from Node import Node, sumOfbyzantine
from Block import Block
from Info import Info, deserialize

# The following two arrays record the relative storage space spent by full storage strategy and our solution (HCSIC) for comparison
myStorage = []
fullStorage = []

# Number of runs (each run will increase the number of nodes by one)
RUNTIME = 19
for nodesNum in range(RUNTIME):
    # If the number of nodes is less than 3, there is no need to form a blockchain network
    if nodesNum < 3:
        myStorage.append(0)
        fullStorage.append(0)
        continue

    # Node Num
    NodesNum = nodesNum

    # For convenience, we assume that each node contributes one IOT information
    IOTInfosNum = NodesNum

    # --------------------BEGIN NOW-----------------
    # STEP1: initialization
    # 1.1: Initialize nodes

    # Node array
    Nodes = []

    for i in range(NodesNum):
        # Generate NodeNum virtual nodes
        if i+1 <= NodesNum*0.9:
            Nodes.append(Node(i, False))
        else:
            # Assuming that the proportion of malicious nodes is 10%
            Nodes.append(Node(i, True))

    # Counting the number of malicious nodes
    ByzantineNodesNum = sumOfbyzantine(Nodes)

    # 1.2: Initialize IOT information

    # IOT information array
    Infos = []

    # Simulated receiving IOTInfosNum IOT messages
    for i in range(IOTInfosNum):

        # Simulate receiving an IOT message
        '''
        INFO_JSON is the JSON format for receiving IOT messages. For the sake of demonstration, we have constructed a simple structure. Below is a brief introduction to it.
        R(room): The location pointed to by the report
        M(msg): The IoT message
        I(index): The IOT device number that submitted this information
        '''
        INFO_JSON = {
            "R": "1-2-203",
            "M": "fire",
            "I": i,
        },

        INFO_STR = json.dumps(INFO_JSON)
        # Convert it to a string format for storage

        '''
        Add information to the Info array
        Among them, the second parameter initialized by the Info class is the information type (i.e. the corresponding secondary classification of the article)
        For convenience, we use numbers to represent information type
        '''
        Infos.append(Info(INFO_STR, i % NodesNum))

    # STEP2: classification & Harmonize the Size

    # Count the number of different types in Infos
    TypeCount = []

    '''
    Initialize TypeCount array
    According to the requirements of the article, the number of primary classifications needs to be equal to the number of nodes
    In this way, each node only needs to store exactly one primary classification
    '''
    for i in range(NodesNum):
        TypeCount.append(0)

    for info in Infos:
        TypeCount[info.type] += 1

    # Find the maximum number of Types and balance them
    MaxType = TypeCount[TypeCount.index(max(TypeCount))]
    InfoNumNodesGet = MaxType

    # Count each item of TypeCount, and if the element is less than the maximum number, fill in an empty message
    EmptyInfoNum = 0
    for i in range(len(TypeCount)):
        if TypeCount[i] < MaxType:
            EmptyInfoNum += MaxType-TypeCount[i]
            for j in range(MaxType-TypeCount[i]):
                INFO_STR = ' '
                Infos.append(Info(INFO_STR, i))

    # At this point, the message length of each primary class remains constant

    # Readjust the Infos array to arrange it in type order, making it easier for subsequent encoding
    Infos.sort(key=lambda x: x.type)

    # STEP3: Encode

    # Generate a block
    block = Block(Infos)
    # RS encoding all IoT information of the block
    block.GenrSerialData()
    block.EncodeMY(ByzantineNodesNum, InfoNumNodesGet)

    # STEP4: Redundant Data
    '''
    Redundancy values are implemented to facilitate recovery in the event of node failures, allowing for data restoration using the information from other nodes along with the redundancy values.
    '''
    # Determine the number of shards for redundant data
    reduantSlice = math.floor(len(Nodes)/(ByzantineNodesNum+1))
    # Calculate the slice size of each slice
    RedPartsize = len(block.RedundantContent) // reduantSlice
    # Initialize slice index
    RedSliceStart = 0

    # Loop, Slice
    # Part stores shard information
    Part = []
    for i in range(reduantSlice):
        RedSliceEnd = RedSliceStart + RedPartsize
        # If it is the last shard, add all remaining redundant values to the shard
        if i == reduantSlice - 1:
            RedSliceEnd = len(block.RedundantContent)
        Part.append(block.RedundantContent[RedSliceStart:RedSliceEnd])
        # Update starting index
        RedSliceStart = RedSliceEnd

    # STEP5: Shard & Storage
    for i in range(len(Nodes)):
        # Extract a portion of shards from block encoding for storage
        ori = block.EcondedContent[i*InfoNumNodesGet *
                                   block.Datalen:(i+1)*InfoNumNodesGet*block.Datalen]

        # Redundant data sharding storage
        red = Part[i % reduantSlice]

        # 存储各个分片 Storage Them
        Nodes[i].ADDstorage(ori, red, i % reduantSlice, block.Datalen)

    # --------------------END OF MAIN OPERATION-----------------

    # Calculate the relative average storage capacity of nodes

    # Obtain the storage cost of each node and take the average to obtain the storage cost of each node.
    averstore = 0
    for node_ in Nodes:

        averstore += node_.get_storage_size()
    averstore = averstore/len(Nodes)

    myStorage.append(averstore/12)
    # The full storage strategy requires storing the entire complete block
    fullStorage.append(block.getBlockSize()/12)

    print("-----------------------")
    print("NodesNum:", nodesNum)
    # 打印我们的方案
    print("Our scheme：", "  ".join(f"{x:8.3f}" for x in myStorage))
    # 打印完整存储策略，同样使用f-string格式化数字，使其右对齐
    print("Full storage strategy：", "  ".join(
        f"{x:8.3f}" for x in fullStorage))

    '''
    Note: The first three values of the array are 0 because blockchain networks are unnecessary when the number of nodes is less than 3
    Note 2: The numbers in the array are of relative size. Due to system differences, it is not possible to use universal storage space calculate code, so relative size (i.e. the byte length of the array) is used here for identification.
    '''

    # print("-----------------------")
print("The console output shows the number of nodes ranging from 0 to NodeNum. Storage space cost per node")

'''
The following code is an image drawing code using mathplot to compare our solution with the full storage solution
'''
# 创建一个图形
plt.figure()
# 绘制两个数组的折线图
plt.plot(myStorage, label='myStorage(HCSIC)')
plt.plot(fullStorage, label='fullStorage')
# 设置x轴和y轴的标签
plt.xlabel('node num (begin with 3 & The quantity of IoT info is directly proportional to the number of nodes)')
plt.ylabel('storage cost (relative size)')
ax = plt.gca()
ax.set_xlim(3, RUNTIME)
# 设置图表标题
plt.title('fig')
# 显示图表
plt.show()
