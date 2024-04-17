'''
Description: This code simulates the entire process of querying. We traverse the query for each node, take the average value, and obtain the average time it takes to find each piece of information.
'''


from queue import Empty
import sys
import reedsolo
import math
import array
import struct
import time
import matplotlib.pyplot as plt
import random
import string

from Node import Node, sumOfbyzantine
from Block import Block
from Info import Info, deserialize
import json

# This array records the average time required to traverse node information
queryTimeALL = []
# Number of runs (each run will increase the number of nodes by one)
RUNTIME = 18
# To balance immeasurable factors such as system environment as much as possible, each query will be repeated "RepeatTimes" times, taking the average
RepeatTimes = 10
for nodesNum in range(RUNTIME):
    # If the number of nodes is less than 3, there is no need to form a blockchain network
    if nodesNum < 3:
        queryTimeALL.append(0)
        continue

    # Node Num
    NodesNum = nodesNum

    # For convenience, we assume that each node contributes one IOT information
    IOTInfosNum = NodesNum

    # Under the condition of "nodesNum" nodes, the array records the query time of each node
    QueryTimeList = []

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

    # 生成一个2到6位长度的随机字符串
    def generate_random_string(min_length=1, max_length=4):
        length = random.randint(min_length, max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    # Simulated receiving IOTInfosNum IOT messages
    for i in range(IOTInfosNum):

        # Simulate receiving an IOT message
        '''
        To simplify the query, in this code , we set the IoT message as a random simple string
        '''
        # 生成随机字符串
        random_string = generate_random_string()
        INFO_STR = 'NO'+str(i)+':'+random_string
        # Convert it to a string format for storage

        '''
        Add information to the Info array
        Among them, the second parameter initialized by the Info class is the information type (i.e. the corresponding secondary classification of the article)
        For convenience, we use numbers to represent information type
        '''
        Infos.append(Info(INFO_STR, i % NodesNum, 1))

    TimeSatrtEncode = time.time()  # 获取当前时间-计时
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
                INFO_JSON = '  '

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

    # STEP4: Shard & Storage
    for i in range(len(Nodes)):
        # Extract a portion of shards from block encoding for storage
        ori = block.EcondedContent[i*InfoNumNodesGet *
                                   block.Datalen:(i+1)*InfoNumNodesGet*block.Datalen]

        # Redundant data sharding storage
        red = Part[i % reduantSlice]

        # 存储各个分片 Storage Them
        Nodes[i].ADDstorage(ori, red, i % reduantSlice, block.Datalen)

    # --------Begin Timing(Start query)-------------------------
    for queryIndex in range(IOTInfosNum):
        QueryReaptTime = []
        EncodeReaptTime = []

        for repeatTime in range(RepeatTimes):
            TimeStartQuery = time.time()  # Get current time: encoding end time

            QueryStr = "NO"+str(queryIndex)

            '''
                If the current node is a Byzantine node, the query information cannot be directly obtained from the current node.
                Need to collect information & Redundant Value from other nodes to recover original data
            '''
            if Nodes[queryIndex].is_byzantine:
                # print("debug_", queryIndex)
                RecoverData = bytearray(b'')
                # erase_pos records the location of missing information (i.e. the location of information stored by Byzantine nodes)
                erase_pos = []

                # Recovering data from other nodes
                for node in Nodes:
                    RecoverData += node.getStorageOriginal()
                    if node.is_byzantine:
                        for j in range(len(node.storageOriginal)):
                            erase_pos.append(
                                j+node.node_id*InfoNumNodesGet*block.Datalen)

                # print(Nodes[3].RedundantIndex)
                # Recovering data from other nodes(Redundant Value)
                RedNodeSort = sorted(Nodes, key=lambda x: x.RedundantIndex)
                last_index = -1
                for i in range(len(RedNodeSort)):
                    if RedNodeSort[i].RedundantIndex == last_index:
                        continue
                    else:
                        last_index = RedNodeSort[i].RedundantIndex
                        RecoverData += RedNodeSort[i].getStorageRedundant()

                # # for i in range(len(Nodes)):
                # #     print(Nodes[i].getStorageOriginal())

                # # RecoverData += Nodes[0].getStorageRedundant()

                # print(RecoverData)
                # print('-----------')
                # print(erase_pos)

                # decode the message
                DecodeMessage = block.Decode(
                    RecoverData, ByzantineNodesNum, InfoNumNodesGet, erase_pos)

                queryRes = deserialize(
                    DecodeMessage[queryIndex*block.Datalen:(queryIndex+1)*block.Datalen], 1).content

                TimeEndQuery = time.time()

            else:
                queryRes = deserialize(
                    Nodes[queryIndex].getStorageOriginal(), 1).content
                TimeEndQuery = time.time()

            # -------Stop Timing(End query)--------------------
            QueryTime = TimeEndQuery - TimeStartQuery
            print(">> Query Successful✌:", queryRes,
                  "\t Spend time⌛", QueryTime)
            QueryReaptTime.append(QueryTime*1000)
            QueryTimeList.append(sum(QueryReaptTime)/len(QueryReaptTime))

    # Calculate average time consumption
    AverQueryTime = sum(QueryTimeList)/len(QueryTimeList)
    queryTimeALL.append(AverQueryTime)


'''
The following code is an image drawing code using mathplot to demostrate the average time to query information for all nodes
'''
# 创建一个图形
plt.figure()
# 绘制两个数组的折线图
# plt.plot(encodeTimeALL, label='encodeTimeALL')
plt.plot(queryTimeALL, label='queryTimeALL')
# plt.plot(query, label='queryTimeALL')
# 设置x轴和y轴的标签
plt.xlabel('node(begin with 3)')
plt.ylabel('query latency (ms)')
ax = plt.gca()
ax.set_xlim(3, RUNTIME)
plt.ylim(0, 50)
# 设置图表标题
plt.title('fig')
# 显示图表
plt.show()
