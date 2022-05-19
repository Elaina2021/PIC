import  numpy as np
import struct

def bmp2pic(bmp_file_path,pic_file_path):

	'先将位图打开'
	f=open(bmp_file_path,'rb') #打开对应的bmp文件
	'下面部分用来读取BMP位图的基础信息'
	#######################################
	#   前14个字节是bitmap-file header     #
	#######################################
	f_type=str(f.read(2)) #这个就可以用来读取 文件类型 需要读取2个字节
	file_size_byte=f.read(4)# 这个可以用来读取文件的大小 需要读取4个字节,文件的大小
	f.seek(f.tell()+4) # 跳过中间无用的四个字节 保留值，总为0
	file_ofset_byte=f.read(4) # 读取位图数据的偏移量

	#######################################
	#      bitmap-information header      #
	#######################################
	f.seek(f.tell()+4) # 跳过无用的两个字节
	file_wide_byte=f.read(4) #读取宽度字节
	file_height_byte=f.read(4) #读取高度字节
	f.seek(f.tell()+2) ## 跳过中间无用的两个字,节总是1
	file_bitcount_byte=f.read(4) #得到每个像素占位大小,图像的色深



	#下面就是将读取的字节转换成指定的类型
	f_size,=struct.unpack('l',file_size_byte) # 文件大小
	f_ofset,=struct.unpack('l',file_ofset_byte) # 偏移量
	f_wide,=struct.unpack('l',file_wide_byte) # 图像宽度
	f_height,=struct.unpack('l',file_height_byte) # 图像高度
	f_bitcount,=struct.unpack('i',file_bitcount_byte) # 位图深度

	if f_bitcount == 8: #8位图,有调色板
		# '读取颜色表'
		color_table=np.empty(shape=[256,4],dtype=int) # 4个维度分别是 (b,g,r,alpha)
		f.seek(54) #跳过文件信息头和位图信息头 14+40
		for i in range(0,256): # 伪彩色 一共只有256色
			b=struct.unpack('B',f.read(1))[0];
			g = struct.unpack('B', f.read(1))[0];
			r = struct.unpack('B', f.read(1))[0];
			alpha = struct.unpack('B', f.read(1))[0];
			color_table[i][0]=r
			color_table[i][1]=g
			color_table[i][2]=b
			color_table[i][3]=alpha

		#首先对文件指针进行偏移
		f.seek(f_ofset) # 就是直接跳到颜色部分，这里就是14+40+256*4=1078
		#图像为8位伪彩色图像
		img=np.empty(shape=[f_height,f_wide],dtype=int) # shape 512*512*4
		count = 0
		for row in range(0, f_height):
			for col in range(0,f_wide):
				count=count+1
				index=struct.unpack('B',f.read(1))[0] # 就是记录地址
				img[row,col]=index 
			while count %4 !=0:
				f.read(1)
				count=count+1

	else: # 24位真彩图
		f.seek(f_ofset)
		img=np.empty(shape=[f_height,f_wide,3],dtype=int)
		count = 0
		for row in range(f_height):
			for col in range(f_wide):
				count = count + 3
				img[row, col, 0] = struct.unpack('B',f.read(1))[0]
				img[row, col, 1] = struct.unpack('B',f.read(1))[0]
				img[row, col, 2] = struct.unpack('B',f.read(1))[0]
			while count % 4 != 0:  
				f.read(1)
				count = count + 1      


	# 保存为pic
	annotation = 0 # 默认无注释
	if f_bitcount==8:
		file_size = 64+annotation+1024+count
	else:
		file_size = 64+annotation+count
	with open(pic_file_path,'wb') as f:
		f.write(struct.pack('c',b'C')) #彩色图像
		f.write(struct.pack('c',b'M')) # 占位
		f.write(struct.pack('H',annotation)) #注释区字节数，默认无注释# H:unsigned short
		f.write(struct.pack('H',f_wide)) #图像列数写入
		f.write(struct.pack('H',f_height)) #图像行数写入
		f.write(struct.pack('H',0)) #图像列起点为0
		f.write(struct.pack('H',0)) #图像行起点为0
		f.write(struct.pack('H',0)) #12--13字节固定为0

		#######################
		# 其他信息区 # 50bytes #
		#######################
		f.write(struct.pack('I',f_bitcount)) #每个像素占多少bit
		f.write(struct.pack('I',file_size)) #文件大小

		########################
		#        注释区        #
		########################
		for i in range(annotation):
			f.write(struct.pack('c',b'A'))
		
		f.seek(64+annotation) # 移动到图像数据存储区
		if f_bitcount==8:
			for i in range(256): # 调色板，4个维度分别是 (b,g,r,alpha)
				f.write(struct.pack('B',color_table[i, 0]))
				f.write(struct.pack('B',color_table[i, 1]))
				f.write(struct.pack('B',color_table[i, 2]))
				f.write(struct.pack('B',color_table[i, 3]))
			for row in range(f_height):
				for col in range(f_wide):
					f.write(struct.pack('B',img[row,col]))

		else: # 真彩图
			for row in range(f_height):
				for col in range(f_wide):
					f.write(struct.pack('B',img[row,col,0]))
					f.write(struct.pack('B',img[row,col,1]))
					f.write(struct.pack('B',img[row,col,2]))
	print("Successfully convert bmp to pic.")
	print("PIC file saved!")
	


def pic2bmp(pic_file_path,bmp_file_path):

	# pic文件读入
	with open(pic_file_path,'rb') as f:
		f.seek(2)
		annotation, = struct.unpack('H',f.read(2)) #注释区字节数
		f_col, = struct.unpack('H',f.read(2)) #图像列数
		f_row, = struct.unpack('H',f.read(2)) #图像行数
		# 其他参数部分
		f.seek(14)
		f_bitcount, = struct.unpack('I',f.read(4)) # 每个像素占位数
		count=0
		if f_bitcount == 8:  # 8位图,有调色板
			f.seek(64+annotation)  # 直接到图片存储区
			color_table = np.empty(shape=[256, 4], dtype=int)  # 存储调色板数据
			for i in range(256):
				r, = struct.unpack('B', f.read(1))
				g, = struct.unpack('B', f.read(1))
				b, = struct.unpack('B', f.read(1))
				alpha, = struct.unpack('B', f.read(1))
				color_table[i][0] = r
				color_table[i][1] = g
				color_table[i][2] = b
				color_table[i][3] = alpha
			# 读取图像数据
			f.seek(64+annotation+1024)
			img = np.empty(shape=[f_row, f_col], dtype=int)
			
			for row in range(f_row):
				for col in range(f_col):
					count+=1
					index, = struct.unpack('B', f.read(1))
					img[row, col] = index

		else: # 真彩图
			f.seek(64+annotation)  # 跳过文件头
			img = np.empty(shape=[f_row, f_col, 3], dtype=int)
			for row in range(f_row):
				for col in range(f_col):
					count+=3
					img[row, col, 0] = struct.unpack('B', f.read(1))[0]
					img[row, col, 1] = struct.unpack('B', f.read(1))[0]
					img[row, col, 2] = struct.unpack('B', f.read(1))[0]

	# BMP文件写入
	with open(bmp_file_path,'wb') as f:

		if f_bitcount==8:
			f_ofset=54+1024 # 文件头和调色板
			file_size = 54+1024+count
		else:
			f_ofset=54 	
			file_size = 54+count
		f.write(struct.pack('c', b'B'))
		f.write(struct.pack('c', b'M')) 
		f.write(struct.pack('L',file_size)) #写入文件大小
		f.write(struct.pack('h', 0))
		f.write(struct.pack('h', 0))

		f.write(struct.pack('L',f_ofset)) #偏移量
		f.write(struct.pack('L',40))  #信息头大小
		f.write(struct.pack('L', f_col))  # 图片宽度
		f.write(struct.pack('L', f_row))  # 图片高度
		f.write(struct.pack('H',1))
		f.write(struct.pack('H', f_bitcount)) # 每个像素占位数
		f.write(struct.pack('L', 0)) #
		f.write(struct.pack('L', 0))
		# 其他信息，默认用零填充
		f.write(struct.pack('L', 0))
		f.write(struct.pack('L', 0))
		f.write(struct.pack('L', 0))
		f.write(struct.pack('L', 0))

		if f_bitcount==8: # 8位图写入
			for i in range(256): #调色板数据写入
				f.write(struct.pack('B', color_table[i][2]))
				f.write(struct.pack('B', color_table[i][1]))
				f.write(struct.pack('B', color_table[i][0]))
				f.write(struct.pack('B', color_table[i][3]))
			count=0
			for row in range(f_row):
				for col in range(f_col):
					count += 1
					f.write(struct.pack('B',img[row,col]))
				while count%4 !=0:
					f.write(struct.pack('B',0))
					count += 1

		else:  # 真彩图
			count = 0
			for row in range(f_row):
				for col in range(f_col):
					count += 3
					f.write(struct.pack('B', img[row, col, 0]))
					f.write(struct.pack('B', img[row, col, 1]))
					f.write(struct.pack('B', img[row, col, 2]))
				while count%4 != 0:
					f.write(struct.pack('B',0))
					count += 1
	print("Successfully convert pic to bmp.")
	print("BMP file saved!")

def read_pic_info(pic_file_path):

    # pic文件读入
    with open(pic_file_path,'rb') as f:
        f_type, = struct.unpack('c',f.read(1)) 
        f.seek(2)
        annotation, = struct.unpack('H',f.read(2)) #注释区字节数
        f_wide, = struct.unpack('H',f.read(2)) #图像列数
        f_height, = struct.unpack('H',f.read(2)) #图像行数
        # 其他参数部分
        f.seek(14)
        f_bitcount, = struct.unpack('I',f.read(4)) # 每个像素占位数
        file_size, = struct.unpack('I',f.read(4)) # 文件大小

    print("类型:",f_type,"大小:",file_size,"宽度:",f_wide,"高度:",f_height,"位图:",f_bitcount)


def read_bmp_info(bmp_file_path):

    # '将位图打开'
    f=open(bmp_file_path,'rb') #打开对应的文件
    #'读取BMP位图基础信息'
    # 前14个字节是bitmap-file header
    f_type=str(f.read(2)) #这个就可以用来读取 文件类型 需要读取2个字节
    file_size_byte=f.read(4)# 这个可以用来读取文件的大小 需要读取4个字节,文件的大小
    f.seek(f.tell()+4) # 跳过中间无用的四个字节 保留值，总为0
    file_ofset_byte=f.read(4) # 读取位图数据的偏移量

    # bitmap-information header
    f.seek(f.tell()+4) # 跳过无用的两个字节
    file_wide_byte=f.read(4) #读取宽度字节
    file_height_byte=f.read(4) #读取高度字节
    f.seek(f.tell()+2) ## 跳过中间无用的两个字,节总是1
    file_bitcount_byte=f.read(4) #得到每个像素占位大小,图像的色深



    #下面就是将读取的字节转换成指定的类型
    f_size,=struct.unpack('l',file_size_byte)
    f_ofset,=struct.unpack('l',file_ofset_byte)
    f_wide,=struct.unpack('l',file_wide_byte) # 图像宽度
    f_height,=struct.unpack('l',file_height_byte) # 图像高度
    f_bitcount,=struct.unpack('i',file_bitcount_byte) # 位图
    print("类型:",f_type,"大小:",f_size,"位图数据偏移量:",f_ofset,"宽度:",f_wide,"高度:",f_height,"位图:",f_bitcount)


